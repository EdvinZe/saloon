from datetime import date

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
    CurrentBookingDraft,
    ExtractedBookingIntent,
)
from app.modules.booking_ai.availability_actions import (
    AvailabilityCheckResult,
    check_booking_draft_availability,
    find_nearest_options,
    master_name,
    minutes_from_hhmm,
    normalize_hhmm,
    parse_booking_date,
    should_check_availability,
)
from app.modules.booking_ai.draft import (
    format_booking_details,
    get_missing_fields,
    get_next_action,
    has_booking_details,
    has_complete_booking_details,
    is_useful_value,
    merge_booking_draft,
)
from app.modules.booking_ai.flexible_availability import (
    apply_explicit_flexible_criteria,
    build_flexible_availability_response,
)
from app.modules.booking_ai.followups import build_followup_response
from app.modules.booking_ai.response_actions import build_prefill_actions
from app.modules.booking_ai.response_messages import (
    build_assistant_message,
    build_assistant_services,
    build_services_list_message,
    build_single_service_message,
    format_service_names,
    format_service_price,
)
from app.modules.booking_ai.schemas import BookingAssistantAction, BookingIntentResponse
from app.modules.booking_ai.master_info import build_master_info_response
from app.modules.booking_ai.service_matching import (
    is_service_name_match,
    match_public_services_by_name,
    normalize_service_match_text,
    normalize_text,
    resolve_service_query,
)
from app.modules.masters.service import list_public_masters
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
    masters = list_public_masters(db)
    master_names = [
        f"{master.first_name} {master.last_name}".strip()
        for master in masters
        if master.first_name or master.last_name
    ]

    local_response = build_local_pre_ai_response(
        db=db,
        user_message=normalized_message,
        current_draft=current_booking_draft,
    )
    if local_response is not None:
        return local_response

    try:
        result = ai_client.extract_booking_intent(
            user_message=normalized_message,
            today=date.today(),
            service_names=service_names,
            master_names=master_names,
            conversation_messages=conversation_messages or [],
            current_booking_draft=current_booking_draft,
        )
    except (AIDisabledError, AIRateLimitError, AIProviderQuotaError, AIProviderError):
        return build_ai_unavailable_response()

    return build_booking_intent_response(db, result, current_booking_draft, normalized_message)


def build_local_pre_ai_response(
    *,
    db: Session,
    user_message: str,
    current_draft: CurrentBookingDraft | None,
) -> BookingIntentResponse | None:
    if is_greeting_message(user_message):
        return BookingIntentResponse(
            intent=BookingIntent.greeting,
            booking_draft=CurrentBookingDraft(),
            assistant_message="Hi! I can help you check services, masters, or available booking times.",
            actions=[],
        )

    if current_draft is None or not is_pending_flexible_service_question(current_draft):
        return build_followup_response(
            db,
            user_message=user_message,
            current_draft=current_draft,
        )

    services = list_public_services(db)
    service_matches = match_public_services_by_name(services, user_message)
    if len(service_matches) == 1:
        service = service_matches[0]
        updated_draft = CurrentBookingDraft.model_validate({
            **current_draft.model_dump(),
            "service_query": service.name,
            "service_id": service.id,
        })
        return build_flexible_availability_response(db, updated_draft)

    if len(service_matches) > 1:
        return BookingIntentResponse(
            intent=BookingIntent.flexible_availability_search,
            booking_draft=current_draft,
            assistant_message=(
                f"I found a few matching services: {format_service_names(service_matches)}. "
                "Which one do you mean?"
            ),
            services=build_assistant_services(service_matches),
            actions=[],
        )

    return BookingIntentResponse(
        intent=BookingIntent.flexible_availability_search,
        booking_draft=current_draft,
        assistant_message=f"I couldn't find that service. Available services are: {format_service_names(services)}.",
        services=build_assistant_services(services),
        actions=[],
    )


def is_pending_flexible_service_question(draft: CurrentBookingDraft) -> bool:
    return not draft.service_query and has_flexible_search_details(draft)


def is_greeting_message(message: str) -> bool:
    normalized = normalize_text(message)
    return normalized in {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}


def build_ai_unavailable_response() -> BookingIntentResponse:
    return BookingIntentResponse(
        intent=BookingIntent.unknown,
        booking_draft=CurrentBookingDraft(),
        assistant_message=(
            "AI assistant is temporarily unavailable right now, but the booking system is still working normally. "
            "You can continue by using the booking form."
        ),
        actions=[
            BookingAssistantAction(
                type="open_booking_form",
                label="Book manually",
            )
        ],
    )


def build_booking_intent_response(
    db: Session,
    extracted: ExtractedBookingIntent,
    current_draft: CurrentBookingDraft | None,
    user_message: str,
) -> BookingIntentResponse:
    followup_response = build_followup_response(
        db,
        user_message=user_message,
        current_draft=current_draft,
    )
    if followup_response is not None:
        return followup_response

    booking_draft = merge_booking_draft(current_draft, extracted)
    if extracted.intent == BookingIntent.flexible_availability_search:
        booking_draft = apply_explicit_flexible_criteria(booking_draft, user_message)
    if should_route_to_flexible_availability(extracted, current_draft, booking_draft):
        return build_flexible_availability_response(db, booking_draft)

    if extracted.intent in {BookingIntent.list_services, BookingIntent.service_info}:
        return build_service_info_response(db, extracted)
    if extracted.intent in {
        BookingIntent.list_masters,
        BookingIntent.master_info,
        BookingIntent.master_service_info,
    }:
        return build_master_info_response(db, extracted)

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
        master_query=booking_draft.master_query,
        date=booking_draft.date,
        start_date=booking_draft.start_date,
        end_date=booking_draft.end_date,
        date_range_type=booking_draft.date_range_type,
        weekdays=booking_draft.weekdays,
        time_preference=booking_draft.time_preference,
        time_preference_type=booking_draft.time_preference_type,
        time=booking_draft.time,
        end_time=booking_draft.end_time,
        daypart=booking_draft.daypart,
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


def should_route_to_flexible_availability(
    extracted: ExtractedBookingIntent,
    current_draft: CurrentBookingDraft | None,
    booking_draft: CurrentBookingDraft,
) -> bool:
    if extracted.intent == BookingIntent.flexible_availability_search:
        return True
    if current_draft is None:
        return False
    if not has_flexible_search_details(current_draft):
        return False
    return bool(booking_draft.service_query)


def has_flexible_search_details(draft: CurrentBookingDraft) -> bool:
    return bool(
        draft.date_range_type
        or draft.start_date
        or draft.end_date
        or draft.weekdays
        or draft.daypart
    )


def build_service_info_response(
    db: Session,
    extracted: ExtractedBookingIntent,
) -> BookingIntentResponse:
    services = list_public_services(db)
    service_query = extracted.service_query

    if extracted.intent == BookingIntent.list_services or not service_query:
        assistant_services = build_assistant_services(services)
        return BookingIntentResponse(
            intent=BookingIntent.list_services,
            service_query=service_query,
            assistant_message=build_services_list_message(services),
            services=assistant_services,
            actions=[],
        )

    matches = match_public_services_by_name(services, service_query)
    if len(matches) == 1:
        service = matches[0]
        return BookingIntentResponse(
            intent=BookingIntent.service_info,
            service_query=service.name,
            assistant_message=build_single_service_message(service),
            services=build_assistant_services([service]),
            actions=[],
        )

    if len(matches) > 1:
        matched_names = format_service_names(matches)
        return BookingIntentResponse(
            intent=BookingIntent.service_info,
            service_query=service_query,
            assistant_message=f"I found a few matching services: {matched_names}. Which one do you mean?",
            services=build_assistant_services(matches),
            actions=[],
        )

    available_names = format_service_names(services)
    return BookingIntentResponse(
        intent=BookingIntent.service_info,
        service_query=service_query,
        assistant_message=f"I couldn't find that service. Available services are: {available_names}.",
        services=build_assistant_services(services),
        actions=[],
    )
