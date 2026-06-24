from app.ai.schemas import (
    BookingIntent,
    BookingNextAction,
    CurrentBookingDraft,
    ExtractedBookingIntent,
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
        "master_query",
        "date",
        "start_date",
        "end_date",
        "date_range_type",
        "weekdays",
        "time",
        "end_time",
        "time_preference",
        "time_preference_type",
        "daypart",
        "limit",
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
    if isinstance(value, list):
        return bool(value)
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
