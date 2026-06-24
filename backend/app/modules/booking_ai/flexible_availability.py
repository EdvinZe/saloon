from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.ai.schemas import (
    BookingDraftAvailabilityOption,
    BookingIntent,
    BookingNextAction,
    CurrentBookingDraft,
)
from app.modules.availability.service import list_available_masters, list_available_slots
from app.modules.booking_ai.availability_actions import minutes_from_hhmm
from app.modules.booking_ai.master_info import (
    format_master_names,
    master_full_name,
    match_public_masters_by_name,
)
from app.modules.booking_ai.response_messages import format_service_names
from app.modules.booking_ai.schemas import (
    BookingAssistantAction,
    BookingAssistantActionPayload,
    BookingAssistantMessageActionPayload,
    BookingAvailabilityOption,
    BookingIntentResponse,
)
from app.modules.booking_ai.service_matching import match_public_services_by_name
from app.modules.masters.models import Master
from app.modules.masters.service import list_public_masters
from app.modules.services.models import Service
from app.modules.services.service import list_public_services

DEFAULT_LIMIT = 3
MAX_LIMIT = 5
DATE_RANGE_MAX_DAYS = 14
NEAREST_SEARCH_DAYS = 14
DAYPART_RANGES = {
    "morning": ("09:00", "12:00"),
    "afternoon": ("12:00", "17:00"),
    "evening": ("17:00", "20:00"),
}
WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def build_flexible_availability_response(
    db: Session,
    draft: CurrentBookingDraft,
    *,
    offset: int | None = None,
    direction: str | None = None,
    exclude_master_ids: list[int] | None = None,
) -> BookingIntentResponse:
    services = list_public_services(db)
    service = resolve_service(services, draft.service_query)
    if service is None:
        return BookingIntentResponse(
            intent=BookingIntent.flexible_availability_search,
            service_query=draft.service_query,
            booking_draft=draft,
            missing_fields=["service"] if not draft.service_query else [],
            next_action=BookingNextAction.ask_service,
            assistant_message=(
                "What service are you looking for?"
                if not draft.service_query
                else f"I couldn't find that service. Available services are: {format_service_names(services)}."
            ),
            actions=[],
        )

    masters = list_public_masters(db)
    master = None
    if draft.master_query:
        master_matches = match_public_masters_by_name(masters, draft.master_query)
        if len(master_matches) != 1:
            message = (
                f"I found a few matching masters: {format_master_names(master_matches)}. Which one do you mean?"
                if master_matches
                else f"I couldn't find that master. Available masters are: {format_master_names(masters)}."
            )
            return BookingIntentResponse(
                intent=BookingIntent.flexible_availability_search,
                service_query=service.name,
                master_query=draft.master_query,
                booking_draft=draft,
                assistant_message=message,
                actions=[],
            )
        master = master_matches[0]

    dates = build_search_dates(draft, today=date.today())
    if not dates:
        return BookingIntentResponse(
            intent=BookingIntent.flexible_availability_search,
            service_query=service.name,
            master_query=draft.master_query,
            booking_draft=draft,
            missing_fields=["date"],
            next_action=BookingNextAction.ask_date,
            assistant_message="What day or date range should I check?",
            actions=[],
        )

    limit = normalize_limit(draft.limit)
    option_offset = draft.shown_option_count if offset is None else offset
    options, has_more = find_flexible_options(
        db=db,
        service=service,
        dates=dates,
        draft=draft,
        master=master,
        limit=limit,
        offset=option_offset,
        direction=direction,
        exclude_master_ids=exclude_master_ids or [],
    )
    actions = build_flexible_actions(options, has_more=has_more)
    last_options = [
        BookingDraftAvailabilityOption.model_validate(option.model_dump())
        for option in options
    ]
    shown_option_count = option_offset + len(options) if options else draft.shown_option_count
    updated_draft = CurrentBookingDraft.model_validate({
        **draft.model_dump(),
        "service_query": service.name,
        "service_id": service.id,
        "master_query": master_full_name(master) if master else draft.master_query,
        "master_id": master.id if master else draft.master_id,
        "master_name": master_full_name(master) if master else draft.master_name,
        "last_intent": BookingIntent.flexible_availability_search.value,
        "last_available_options": last_options,
        "shown_option_count": shown_option_count,
        "excluded_master_ids": exclude_master_ids or draft.excluded_master_ids,
    })

    return BookingIntentResponse(
        intent=BookingIntent.flexible_availability_search,
        service_query=service.name,
        master_query=updated_draft.master_query,
        date=updated_draft.date,
        start_date=updated_draft.start_date,
        end_date=updated_draft.end_date,
        date_range_type=updated_draft.date_range_type,
        weekdays=updated_draft.weekdays,
        time_preference=updated_draft.time_preference,
        time_preference_type=updated_draft.time_preference_type,
        time=updated_draft.time,
        end_time=updated_draft.end_time,
        daypart=updated_draft.daypart,
        booking_draft=updated_draft,
        next_action=(
            BookingNextAction.availability_options_found
            if options
            else BookingNextAction.availability_alternatives
        ),
        assistant_message=build_flexible_availability_message(
            service=service,
            draft=updated_draft,
            options=options,
            direction=direction,
            offset=option_offset,
        ),
        available_options=options,
        actions=actions,
    )


def resolve_service(services: list[Service], service_query: str | None) -> Service | None:
    if not service_query:
        return None
    matches = match_public_services_by_name(services, service_query)
    if len(matches) == 1:
        return matches[0]
    return None


def build_search_dates(draft: CurrentBookingDraft, *, today: date) -> list[date]:
    range_type = (draft.date_range_type or "").strip().lower()
    if range_type in {"today", "single_day"} and draft.date:
        selected = parse_iso_date(draft.date)
        return [selected] if selected else []
    if range_type == "tomorrow" and draft.date:
        selected = parse_iso_date(draft.date)
        return [selected] if selected else []
    if draft.date and not range_type:
        selected = parse_iso_date(draft.date)
        return [selected] if selected else []
    if range_type == "nearest":
        return date_span(today, today + timedelta(days=NEAREST_SEARCH_DAYS))
    if range_type == "this_week":
        return date_span(today, today + timedelta(days=6 - today.weekday()))
    if range_type == "next_week":
        start = today + timedelta(days=(7 - today.weekday()))
        return date_span(start, start + timedelta(days=6))
    if range_type == "weekend":
        if today.weekday() == 6:
            return [today]
        saturday = today + timedelta(days=(5 - today.weekday()) % 7)
        return [saturday, saturday + timedelta(days=1)]
    if range_type == "weekdays":
        return build_weekday_dates(draft, today=today)
    if range_type == "date_range":
        start = parse_iso_date(draft.start_date)
        end = parse_iso_date(draft.end_date)
        if start is None or end is None:
            return []
        return date_span(start, min(end, start + timedelta(days=DATE_RANGE_MAX_DAYS - 1)))
    return []


def build_weekday_dates(draft: CurrentBookingDraft, *, today: date) -> list[date]:
    selected_weekdays = {
        WEEKDAYS[item]
        for item in (draft.weekdays or [])
        if item in WEEKDAYS
    } or {0, 1, 2, 3, 4}

    start = parse_iso_date(draft.start_date) or today
    end = parse_iso_date(draft.end_date)
    if end is None:
        if today.weekday() <= 4:
            end = today + timedelta(days=4 - today.weekday())
        else:
            start = today + timedelta(days=(7 - today.weekday()))
            end = start + timedelta(days=4)

    return [
        value
        for value in date_span(start, min(end, start + timedelta(days=DATE_RANGE_MAX_DAYS - 1)))
        if value.weekday() in selected_weekdays
    ]


def date_span(start: date, end: date) -> list[date]:
    if end < start:
        return []
    day_count = (end - start).days + 1
    return [start + timedelta(days=offset) for offset in range(day_count)]


def parse_iso_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def find_flexible_options(
    *,
    db: Session,
    service: Service,
    dates: list[date],
    draft: CurrentBookingDraft,
    master: Master | None,
    limit: int,
    offset: int = 0,
    direction: str | None = None,
    exclude_master_ids: list[int] | None = None,
) -> tuple[list[BookingAvailabilityOption], bool]:
    options: list[BookingAvailabilityOption] = []
    skipped = 0
    excluded = set(exclude_master_ids or [])
    earlier_boundary = None
    if direction == "earlier" and draft.last_available_options:
        first_option = draft.last_available_options[0]
        earlier_boundary = (first_option.date, first_option.time)
    ordered_dates = list(reversed(dates)) if direction == "earlier" else dates

    for selected_date in ordered_dates:
        slots = list_available_slots(
            db=db,
            service_id=service.id,
            selected_date=selected_date,
        )
        slot_list = list(reversed(slots)) if direction == "earlier" else slots
        for slot in slot_list:
            if slot.status != "free" or not slot_matches_time_filter(slot.time, draft):
                continue

            available_masters = list_available_masters(
                db=db,
                service_id=service.id,
                selected_date=selected_date,
                selected_time=slot.time,
            )
            if master is not None:
                available_masters = [
                    available_master
                    for available_master in available_masters
                    if available_master.id == master.id
                ]
            if excluded:
                available_masters = [
                    available_master
                    for available_master in available_masters
                    if available_master.id not in excluded
                ]
            if not available_masters:
                continue

            available_master = available_masters[0]
            option = BookingAvailabilityOption(
                service_id=service.id,
                service_name=service.name,
                master_id=available_master.id,
                master_name=master_full_name(available_master),
                date=selected_date.isoformat(),
                time=slot.time,
            )
            if earlier_boundary is not None and (option.date, option.time) >= earlier_boundary:
                continue
            if skipped < offset:
                skipped += 1
                continue
            if len(options) >= limit:
                return (list(reversed(options)) if direction == "earlier" else options), True

            options.append(option)

    if direction == "earlier":
        options = list(reversed(options))
    return options, False


def slot_matches_time_filter(slot_time: str, draft: CurrentBookingDraft) -> bool:
    slot_minutes = minutes_from_hhmm(slot_time)
    start_time, end_time = time_bounds_for_draft(draft)

    if start_time is not None and slot_minutes < minutes_from_hhmm(start_time):
        return False
    if end_time is not None and slot_minutes >= minutes_from_hhmm(end_time):
        return False

    preference_type = draft.time_preference_type
    if preference_type in {"after", "before", "at", "exact", "between", "any", None}:
        return True
    return True


def time_bounds_for_draft(draft: CurrentBookingDraft) -> tuple[str | None, str | None]:
    if draft.daypart in DAYPART_RANGES:
        return DAYPART_RANGES[draft.daypart]

    preference_type = draft.time_preference_type
    if preference_type == "after" and draft.time:
        return draft.time, None
    if preference_type == "before" and draft.time:
        return None, draft.time
    if preference_type == "between" and draft.time and draft.end_time:
        return draft.time, draft.end_time
    if preference_type in {"at", "exact"} and draft.time:
        return draft.time, add_minutes_hhmm(draft.time, 1)
    return None, None


def add_minutes_hhmm(value: str, minutes: int) -> str:
    total = minutes_from_hhmm(value) + minutes
    return f"{total // 60:02d}:{total % 60:02d}"


def normalize_limit(value: int | None) -> int:
    if value is None:
        return DEFAULT_LIMIT
    return max(1, min(value, MAX_LIMIT))


def build_flexible_actions(
    options: list[BookingAvailabilityOption],
    *,
    has_more: bool = False,
) -> list[BookingAssistantAction]:
    actions = build_flexible_prefill_actions(options)
    if has_more:
        actions.append(
            BookingAssistantAction(
                type="send_message",
                label="Show more options",
                payload=BookingAssistantMessageActionPayload(message="show more"),
            )
        )
    actions.extend([
        BookingAssistantAction(type="open_booking_form", label="Open booking form"),
        BookingAssistantAction(
            type="reset_ai_draft",
            label="Start over",
            payload=BookingAssistantMessageActionPayload(message="start over"),
        ),
    ])
    return actions


def build_flexible_prefill_actions(
    options: list[BookingAvailabilityOption],
) -> list[BookingAssistantAction]:
    return [
        BookingAssistantAction(
            label=f"Use {format_action_date(option.date)} {option.time}",
            payload=BookingAssistantActionPayload(
                service_id=option.service_id,
                master_id=option.master_id,
                date=option.date,
                time=option.time,
            ),
        )
        for option in options
    ]


def build_flexible_availability_message(
    *,
    service: Service,
    draft: CurrentBookingDraft,
    options: list[BookingAvailabilityOption],
    direction: str | None = None,
    offset: int = 0,
) -> str:
    criteria = describe_flexible_criteria(draft)
    if not options:
        if direction == "earlier":
            return "I couldn't find earlier matching slots. You can try another date or use the booking form."
        if offset:
            return "I don't see more matching slots for that search. You can try another date or use the booking form."
        return (
            f"I couldn't find {service.name} slots{criteria}. "
            "You can try another time or check the booking form."
        )

    options_text = "; ".join(
        f"{format_option_date(option.date)} {option.time} - {option.master_name}"
        for option in options
    )
    if direction == "later" or offset:
        return f"Here are more {service.name} slots{criteria}: {options_text}."
    if direction == "earlier":
        return f"Here are earlier {service.name} slots{criteria}: {options_text}."
    return f"I found these {service.name} slots{criteria}: {options_text}."


def describe_flexible_criteria(draft: CurrentBookingDraft) -> str:
    parts = []
    time_text = describe_time_filter(draft)
    date_text = describe_date_filter(draft)
    if time_text:
        parts.append(time_text)
    if date_text:
        parts.append(date_text)
    if draft.master_query:
        parts.append(f"with {draft.master_query}")
    return f" {' '.join(parts)}" if parts else ""


def describe_time_filter(draft: CurrentBookingDraft) -> str:
    if draft.daypart:
        return draft.daypart
    if draft.time_preference_type == "after" and draft.time:
        return f"after {draft.time}"
    if draft.time_preference_type == "before" and draft.time:
        return f"before {draft.time}"
    if draft.time_preference_type == "between" and draft.time and draft.end_time:
        return f"between {draft.time} and {draft.end_time}"
    if draft.time_preference_type in {"at", "exact"} and draft.time:
        return f"at {draft.time}"
    return ""


def describe_date_filter(draft: CurrentBookingDraft) -> str:
    range_type = draft.date_range_type
    if range_type in {"today", "tomorrow", "this_week", "next_week", "weekend", "weekdays", "nearest"}:
        return range_type.replace("_", " ")
    if draft.date:
        return f"on {draft.date}"
    if draft.start_date and draft.end_date:
        return f"from {draft.start_date} to {draft.end_date}"
    return ""


def format_option_date(value: str) -> str:
    selected = date.fromisoformat(value)
    return selected.strftime("%A")


def format_action_date(value: str) -> str:
    selected = date.fromisoformat(value)
    return selected.strftime("%a")
