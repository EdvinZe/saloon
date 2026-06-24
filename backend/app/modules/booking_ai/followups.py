from sqlalchemy.orm import Session

from app.ai.schemas import BookingIntent, CurrentBookingDraft
from app.modules.booking_ai.flexible_availability import build_flexible_availability_response
from app.modules.booking_ai.schemas import (
    BookingAssistantAction,
    BookingAssistantMessageActionPayload,
    BookingIntentResponse,
)

SHOW_MORE_COMMANDS = {"show more", "more options", "another time"}
LATER_COMMANDS = {"later"}
EARLIER_COMMANDS = {"earlier"}
OTHER_MASTER_COMMANDS = {"other master", "another master"}
BOOK_MANUALLY_COMMANDS = {"book manually", "open booking form"}
START_OVER_COMMANDS = {"start over", "reset"}


def build_followup_response(
    db: Session,
    *,
    user_message: str,
    current_draft: CurrentBookingDraft | None,
) -> BookingIntentResponse | None:
    command = normalize_command(user_message)
    if command in BOOK_MANUALLY_COMMANDS:
        return BookingIntentResponse(
            intent=BookingIntent.unknown,
            booking_draft=current_draft or CurrentBookingDraft(),
            assistant_message="Sure - you can continue in the booking form.",
            actions=[
                BookingAssistantAction(
                    type="open_booking_form",
                    label="Open booking form",
                )
            ],
        )
    if command in START_OVER_COMMANDS:
        return BookingIntentResponse(
            intent=BookingIntent.unknown,
            booking_draft=CurrentBookingDraft(),
            assistant_message="Sure - let's start over. What service are you looking for?",
            actions=[
                BookingAssistantAction(
                    type="reset_ai_draft",
                    label="Start over",
                    payload=BookingAssistantMessageActionPayload(message="start over"),
                )
            ],
        )

    if current_draft is None or current_draft.last_intent != BookingIntent.flexible_availability_search.value:
        return None

    if command in SHOW_MORE_COMMANDS or command in LATER_COMMANDS:
        return build_flexible_availability_response(
            db,
            current_draft,
            offset=current_draft.shown_option_count,
            direction="later" if command in LATER_COMMANDS else None,
        )
    if command in EARLIER_COMMANDS:
        return build_flexible_availability_response(
            db,
            current_draft,
            offset=0,
            direction="earlier",
        )
    if command in OTHER_MASTER_COMMANDS:
        excluded_master_ids = master_ids_from_last_options(current_draft)
        search_draft = CurrentBookingDraft.model_validate({
            **current_draft.model_dump(),
            "master_query": None,
            "master_id": None,
            "master_name": None,
        })
        response = build_flexible_availability_response(
            db,
            search_draft,
            offset=0,
            exclude_master_ids=excluded_master_ids,
        )
        if response.available_options:
            return response
        return BookingIntentResponse(
            intent=BookingIntent.flexible_availability_search,
            booking_draft=current_draft,
            assistant_message=(
                "I couldn't find another master for the same criteria. "
                "You can choose one of the available options or try another time."
            ),
            actions=[
                BookingAssistantAction(
                    type="open_booking_form",
                    label="Open booking form",
                )
            ],
        )

    return None


def master_ids_from_last_options(draft: CurrentBookingDraft) -> list[int]:
    ids = []
    for option in draft.last_available_options:
        if option.master_id not in ids:
            ids.append(option.master_id)
    return ids


def normalize_command(value: str) -> str:
    return " ".join(value.strip().lower().split())
