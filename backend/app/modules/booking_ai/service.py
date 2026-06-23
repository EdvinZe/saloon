from datetime import date
import re

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ai.client import (
    AIDisabledError,
    AIProviderError,
    AIProviderQuotaError,
    AIRateLimitError,
    ai_client,
)
from app.ai.schemas import (
    BookingConversationMessage,
    BookingIntent,
    BookingNextAction,
    CurrentBookingDraft,
    ExtractedBookingIntent,
)
from app.modules.availability.service import list_available_masters, list_available_slots
from app.modules.booking_ai.schemas import (
    BookingAssistantAction,
    BookingAssistantActionPayload,
    BookingAvailabilityOption,
    BookingIntentResponse,
    BookingNearestAvailabilityOption,
)
from app.modules.services.models import Service
from app.modules.services.service import list_public_services


def extract_booking_intent(
    db: Session,
    message: str,
    conversation_messages: list[BookingConversationMessage] | None = None,
    current_booking_draft: CurrentBookingDraft | None = None,
) -> BookingIntentResponse:
    normalized_message = message.strip()
    if not normalized_message:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Message must not be empty",
        )

    services = list_public_services(db)
    service_names = [service.name for service in services if service.name]

    try:
        result = ai_client.extract_booking_intent(
            user_message=normalized_message,
            today=date.today(),
            service_names=service_names,
            conversation_messages=conversation_messages or [],
            current_booking_draft=current_booking_draft,
        )
    except AIDisabledError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except AIRateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
        ) from exc
    except AIProviderQuotaError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="AI provider quota is temporarily exhausted",
        ) from exc
    except AIProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI provider is temporarily unavailable",
        ) from exc

    return build_booking_intent_response(db, result, current_booking_draft, normalized_message)


def build_booking_intent_response(
    db: Session,
    extracted: ExtractedBookingIntent,
    current_draft: CurrentBookingDraft | None,
    user_message: str,
) -> BookingIntentResponse:
    booking_draft = merge_booking_draft(current_draft, extracted)
    missing_fields = get_missing_fields(booking_draft, extracted.intent)
    next_action = get_next_action(booking_draft, extracted.intent, missing_fields)
    availability_result = None

    if should_check_availability(
        booking_draft=booking_draft,
        intent=extracted.intent,
        user_message=user_message,
        missing_fields=missing_fields,
    ):
        availability_result = check_booking_draft_availability(db, booking_draft)
        booking_draft = availability_result.booking_draft
        next_action = availability_result.next_action

    assistant_message = build_assistant_message(
        booking_draft=booking_draft,
        intent=extracted.intent,
        missing_fields=missing_fields,
        user_message=user_message,
        availability_result=availability_result,
    )

    return BookingIntentResponse(
        intent=extracted.intent,
        service_query=booking_draft.service_query,
        date=booking_draft.date,
        time_preference=booking_draft.time_preference,
        time_preference_type=booking_draft.time_preference_type,
        time=booking_draft.time,
        master_preference=booking_draft.master_preference,
        booking_draft=booking_draft,
        missing_fields=missing_fields,
        next_action=next_action,
        assistant_message=assistant_message,
        requested_time_available=availability_result.requested_time_available if availability_result else None,
        available_options=availability_result.available_options if availability_result else [],
        nearest_options=availability_result.nearest_options if availability_result else [],
        actions=availability_result.actions if availability_result else [],
    )


def merge_booking_draft(
    current_draft: CurrentBookingDraft | None,
    extracted: ExtractedBookingIntent,
) -> CurrentBookingDraft:
    draft = CurrentBookingDraft.model_validate(
        current_draft.model_dump() if current_draft else {}
    )

    for field_name in (
        "service_query",
        "service_id",
        "date",
        "time",
        "time_preference",
        "time_preference_type",
        "master_preference",
        "master_id",
        "master_name",
    ):
        value = getattr(extracted, field_name, None)
        if is_useful_value(value):
            setattr(draft, field_name, value)

    if draft.time and not draft.time_preference:
        draft.time_preference = f"at {draft.time}"
    if draft.time and not draft.time_preference_type:
        draft.time_preference_type = "at"

    return CurrentBookingDraft.model_validate(draft.model_dump())


def is_useful_value(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip()) and value.strip().lower() != "unknown"
    return True


def get_missing_fields(
    draft: CurrentBookingDraft,
    intent: BookingIntent,
) -> list[str]:
    if intent in {BookingIntent.greeting, BookingIntent.unknown, BookingIntent.unsupported}:
        return []

    missing_fields: list[str] = []
    if not draft.service_query:
        missing_fields.append("service")
    if not draft.date:
        missing_fields.append("date")
    if not draft.time and not draft.time_preference:
        missing_fields.append("time")
    return missing_fields


def get_next_action(
    draft: CurrentBookingDraft,
    intent: BookingIntent,
    missing_fields: list[str],
) -> BookingNextAction:
    if intent == BookingIntent.unsupported:
        return BookingNextAction.unsupported
    if missing_fields:
        first_missing = missing_fields[0]
        if first_missing == "service":
            return BookingNextAction.ask_service
        if first_missing == "date":
            return BookingNextAction.ask_date
        if first_missing == "time":
            return BookingNextAction.ask_time
    if draft.service_query and draft.date and (draft.time or draft.time_preference):
        return BookingNextAction.ready_to_check_availability
    return BookingNextAction.none


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


def resolve_service_query(db: Session, service_query: str | None) -> Service | None:
    if not service_query:
        return None

    normalized_query = normalize_text(service_query)
    services = list_public_services(db)

    for service in services:
        if normalize_text(service.name) == normalized_query:
            return service

    for service in services:
        service_name = normalize_text(service.name)
        if normalized_query in service_name or service_name in normalized_query:
            return service

    for service in services:
        service_description = normalize_text(service.description or "")
        if service_description and (
            normalized_query in service_description or service_description in normalized_query
        ):
            return service

    return None


def normalize_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


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


def build_prefill_actions(
    options: list[BookingAvailabilityOption],
    *,
    use_option_labels: bool = False,
) -> list[BookingAssistantAction]:
    actions: list[BookingAssistantAction] = []
    for option in options:
        label = "Continue booking"
        if use_option_labels:
            label = f"Use {option.time}"
        elif len(options) > 1:
            label = f"Book with {option.master_name} at {option.time}"

        actions.append(
            BookingAssistantAction(
                label=label,
                payload=BookingAssistantActionPayload(
                    service_id=option.service_id,
                    master_id=option.master_id,
                    date=option.date,
                    time=option.time,
                ),
            )
        )
    return actions


def minutes_from_hhmm(value: str) -> int:
    hour, minute = value.split(":", 1)
    return int(hour) * 60 + int(minute)


def master_name(master) -> str:
    return f"{master.first_name} {master.last_name}".strip()


def build_assistant_message(
    *,
    booking_draft: CurrentBookingDraft,
    intent: BookingIntent,
    missing_fields: list[str],
    user_message: str,
    availability_result: AvailabilityCheckResult | None = None,
) -> str:
    if availability_result is not None:
        if availability_result.error_message:
            return availability_result.error_message
        if availability_result.requested_time_available:
            option_names = ", ".join(
                option.master_name for option in availability_result.available_options
            )
            label = "Available master" if len(availability_result.available_options) == 1 else "Available masters"
            return (
                f"Good news - {booking_draft.service_query} is available on {booking_draft.date} "
                f"at {booking_draft.time}. {label}: {option_names}. "
                "You can continue with the booking form to confirm it."
            )
        if availability_result.nearest_options:
            options_text = " or ".join(
                f"{option.time} with {option.master_name}"
                for option in availability_result.nearest_options
            )
            return (
                f"{booking_draft.time} is not available for {booking_draft.service_query} "
                f"on {booking_draft.date}. The closest available options are {options_text}. "
                "You can continue with the booking form to choose one."
            )
        return (
            f"{booking_draft.time} is not available for {booking_draft.service_query} "
            f"on {booking_draft.date}, and I could not find same-day alternatives. "
            "You can continue with the booking form to choose another time."
        )

    lowered_message = user_message.lower()
    asks_availability = intent == BookingIntent.check_available_masters or any(
        phrase in lowered_message
        for phrase in ("available", "availability", "free", "master can", "what master")
    )

    if intent == BookingIntent.unsupported:
        return "I can help with booking questions, but I cannot access private booking, payment, or admin data."
    if intent == BookingIntent.greeting and not has_booking_details(booking_draft):
        return "Hi! I can help prepare your booking details. What service would you like?"

    if "service" in missing_fields:
        return "What service are you looking for?"
    if "date" in missing_fields:
        return "What date would you like to book?"
    if "time" in missing_fields:
        return "What time would you like to book?"

    if has_complete_booking_details(booking_draft):
        if asks_availability:
            return (
                "I have the booking details. Live availability is handled by the booking system, "
                "so you can continue with the booking form to see available masters and times."
            )
        return (
            f"I understood that you want {format_booking_details(booking_draft)}. "
            "I can help you check matching booking options."
        )

    if has_booking_details(booking_draft):
        return (
            f"I have {format_booking_details(booking_draft)} so far. "
            "Tell me the missing detail and I can prepare the booking request."
        )

    return "How can I help with your booking?"


def has_booking_details(draft: CurrentBookingDraft) -> bool:
    return bool(draft.service_query or draft.date or draft.time or draft.time_preference)


def has_complete_booking_details(draft: CurrentBookingDraft) -> bool:
    return bool(draft.service_query and draft.date and (draft.time or draft.time_preference))


def format_booking_details(draft: CurrentBookingDraft) -> str:
    details = []
    if draft.service_query:
        details.append(draft.service_query)
    if draft.date:
        details.append(f"on {draft.date}")
    if draft.time:
        details.append(f"at {draft.time}")
    elif draft.time_preference:
        details.append(draft.time_preference)
    return " ".join(details)
