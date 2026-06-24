from datetime import date
import re

from sqlalchemy.orm import Session

from app.ai.schemas import BookingIntent, BookingNextAction, CurrentBookingDraft
from app.modules.availability.service import list_available_masters, list_available_slots
from app.modules.booking_ai.draft import has_complete_booking_details
from app.modules.booking_ai.response_actions import build_prefill_actions
from app.modules.booking_ai.schemas import (
    BookingAssistantAction,
    BookingAvailabilityOption,
    BookingNearestAvailabilityOption,
)
from app.modules.booking_ai.service_matching import resolve_service_query
from app.modules.services.models import Service


class AvailabilityCheckResult:
    def __init__(
        self,
        *,
        booking_draft: CurrentBookingDraft,
        next_action: BookingNextAction,
        requested_time_available: bool,
        available_options: list[BookingAvailabilityOption] | None = None,
        nearest_options: list[BookingNearestAvailabilityOption] | None = None,
        actions: list[BookingAssistantAction] | None = None,
        error_message: str | None = None,
    ) -> None:
        self.booking_draft = booking_draft
        self.next_action = next_action
        self.requested_time_available = requested_time_available
        self.available_options = available_options or []
        self.nearest_options = nearest_options or []
        self.actions = actions or []
        self.error_message = error_message


def should_check_availability(
    *,
    booking_draft: CurrentBookingDraft,
    intent: BookingIntent,
    user_message: str,
    missing_fields: list[str],
) -> bool:
    if missing_fields or not has_complete_booking_details(booking_draft):
        return False
    if intent == BookingIntent.check_available_masters:
        return True

    lowered_message = user_message.lower().strip()
    return lowered_message in {"check", "yes", "so"} or any(
        phrase in lowered_message
        for phrase in (
            "check availability",
            "is this time available",
            "do you have time",
            "available",
            "availability",
            "free",
            "master can",
            "what master",
        )
    )


def check_booking_draft_availability(
    db: Session,
    booking_draft: CurrentBookingDraft,
) -> AvailabilityCheckResult:
    service = resolve_service_query(db, booking_draft.service_query)
    if service is None:
        return AvailabilityCheckResult(
            booking_draft=booking_draft,
            next_action=BookingNextAction.ask_service,
            requested_time_available=False,
            error_message="What service are you looking for? Please choose one of the available services.",
        )

    selected_date = parse_booking_date(booking_draft.date)
    selected_time = normalize_hhmm(booking_draft.time)
    if selected_date is None:
        return AvailabilityCheckResult(
            booking_draft=booking_draft,
            next_action=BookingNextAction.ask_date,
            requested_time_available=False,
            error_message="What date would you like to book?",
        )
    if selected_time is None:
        return AvailabilityCheckResult(
            booking_draft=booking_draft,
            next_action=BookingNextAction.ask_time,
            requested_time_available=False,
            error_message="What time would you like to book?",
        )

    updated_draft = CurrentBookingDraft.model_validate({
        **booking_draft.model_dump(),
        "service_query": service.name,
        "service_id": service.id,
        "date": selected_date.isoformat(),
        "time": selected_time,
        "time_preference": f"at {selected_time}",
        "time_preference_type": "at",
    })

    try:
        available_masters = list_available_masters(
            db=db,
            service_id=service.id,
            selected_date=selected_date,
            selected_time=selected_time,
        )
        if available_masters:
            available_options = [
                BookingAvailabilityOption(
                    service_id=service.id,
                    service_name=service.name,
                    master_id=master.id,
                    master_name=master_name(master),
                    date=selected_date.isoformat(),
                    time=selected_time,
                )
                for master in available_masters
            ]
            first_option = available_options[0]
            updated_draft = CurrentBookingDraft.model_validate({
                **updated_draft.model_dump(),
                "master_id": first_option.master_id,
                "master_name": first_option.master_name,
            })
            return AvailabilityCheckResult(
                booking_draft=updated_draft,
                next_action=BookingNextAction.availability_found,
                requested_time_available=True,
                available_options=available_options,
                actions=build_prefill_actions(available_options),
            )

        nearest_options = find_nearest_options(
            db=db,
            service=service,
            selected_date=selected_date,
            requested_time=selected_time,
        )
        return AvailabilityCheckResult(
            booking_draft=updated_draft,
            next_action=BookingNextAction.availability_alternatives,
            requested_time_available=False,
            nearest_options=nearest_options,
            actions=build_prefill_actions(nearest_options, use_option_labels=True),
        )
    except Exception:
        return AvailabilityCheckResult(
            booking_draft=updated_draft,
            next_action=BookingNextAction.ready_to_check_availability,
            requested_time_available=False,
            error_message=(
                "I couldn't check live availability right now, but the booking form is still working. "
                "You can continue there to choose a time."
            ),
        )


def parse_booking_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def normalize_hhmm(value: str | None) -> str | None:
    if not value:
        return None
    match = re.fullmatch(r"([01]?\d|2[0-3])[:.]([0-5]\d)", value.strip())
    if not match:
        return None
    return f"{int(match.group(1)):02d}:{int(match.group(2)):02d}"


def find_nearest_options(
    *,
    db: Session,
    service: Service,
    selected_date: date,
    requested_time: str,
) -> list[BookingNearestAvailabilityOption]:
    slots = list_available_slots(
        db=db,
        service_id=service.id,
        selected_date=selected_date,
    )
    requested_minutes = minutes_from_hhmm(requested_time)
    free_times = [slot.time for slot in slots if slot.status == "free"]
    before = sorted(
        [slot_time for slot_time in free_times if minutes_from_hhmm(slot_time) < requested_minutes],
        key=lambda slot_time: requested_minutes - minutes_from_hhmm(slot_time),
    )[:2]
    after = sorted(
        [slot_time for slot_time in free_times if minutes_from_hhmm(slot_time) > requested_minutes],
        key=lambda slot_time: minutes_from_hhmm(slot_time) - requested_minutes,
    )[:2]

    options: list[BookingNearestAvailabilityOption] = []
    for direction, times in (("before", before), ("after", after)):
        for slot_time in times:
            masters = list_available_masters(
                db=db,
                service_id=service.id,
                selected_date=selected_date,
                selected_time=slot_time,
            )
            if not masters:
                continue
            master = masters[0]
            options.append(
                BookingNearestAvailabilityOption(
                    service_id=service.id,
                    service_name=service.name,
                    master_id=master.id,
                    master_name=master_name(master),
                    date=selected_date.isoformat(),
                    time=slot_time,
                    direction=direction,
                )
            )
    return sorted(
        options,
        key=lambda option: abs(minutes_from_hhmm(option.time) - requested_minutes),
    )


def minutes_from_hhmm(value: str) -> int:
    hour, minute = value.split(":", 1)
    return int(hour) * 60 + int(minute)


def master_name(master) -> str:
    return f"{master.first_name} {master.last_name}".strip()
