from datetime import date
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ai.debug import log_ai_debug
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
    normalize_relative_booking_dates,
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
    request_id: str | None = None,
) -> BookingIntentResponse:
    trace_id = request_id or uuid4().hex
    normalized_message = message.strip()
    if not normalized_message:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Message must not be empty",
        )

    log_ai_debug(
        "ai_booking_request",
        trace_id,
        {
            "message": normalized_message,
            "conversation_messages_count": len(conversation_messages or []),
            "current_booking_draft": current_booking_draft,
        },
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
        log_backend_decision(
            trace_id,
            "build_local_pre_ai_response",
            "local pre-AI response matched incoming message or draft",
        )
        return log_and_return_response(trace_id, local_response)

    request_today = date.today()
    try:
        result = ai_client.extract_booking_intent(
            user_message=normalized_message,
            today=request_today,
            service_names=service_names,
            master_names=master_names,
            conversation_messages=conversation_messages or [],
            current_booking_draft=current_booking_draft,
            request_id=trace_id,
        )
    except (AIDisabledError, AIRateLimitError, AIProviderQuotaError, AIProviderError):
        log_backend_decision(
            trace_id,
            "build_ai_unavailable_response",
            "AI provider unavailable, disabled, rate-limited, or returned an error",
        )
        return log_and_return_response(trace_id, build_ai_unavailable_response())

    log_ai_debug(
        "ai_booking_parsed_intent",
        trace_id,
        extracted_intent_debug_payload(result),
    )
    return build_booking_intent_response(
        db,
        result,
        current_booking_draft,
        normalized_message,
        today=request_today,
        request_id=trace_id,
    )


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


def extracted_intent_debug_payload(extracted: ExtractedBookingIntent) -> dict[str, object]:
    return {
        "intent": extracted.intent,
        "service_query": extracted.service_query,
        "master_query": extracted.master_query,
        "date": extracted.date,
        "start_date": extracted.start_date,
        "end_date": extracted.end_date,
        "date_range_type": extracted.date_range_type,
        "weekdays": extracted.weekdays,
        "time": extracted.time,
        "end_time": extracted.end_time,
        "time_preference": extracted.time_preference,
        "time_preference_type": extracted.time_preference_type,
        "daypart": extracted.daypart,
        "master_preference": extracted.master_preference,
        "missing_fields": extracted.missing_fields,
        "assistant_message": extracted.assistant_message,
    }


def log_backend_decision(request_id: str, handler: str, reason: str) -> None:
    log_ai_debug(
        "ai_booking_backend_decision",
        request_id,
        {
            "handler": handler,
            "reason": reason,
        },
    )


def log_and_return_response(
    request_id: str,
    response: BookingIntentResponse,
) -> BookingIntentResponse:
    log_ai_debug(
        "ai_booking_response",
        request_id,
        {
            "intent": response.intent,
            "assistant_message": response.assistant_message,
            "next_action": response.next_action,
            "missing_fields": response.missing_fields,
            "booking_draft": response.booking_draft,
            "actions_count": len(response.actions),
            "available_options_count": len(response.available_options),
        },
    )
    return response


def backend_decision_reason(
    *,
    availability_result: AvailabilityCheckResult | None,
    missing_fields: list[str],
    next_action: object,
) -> str:
    if availability_result is not None:
        return "availability check completed for known booking details"
    if missing_fields:
        return f"missing required booking fields: {', '.join(missing_fields)}"
    return f"default booking response branch selected with next_action={next_action}"


def build_booking_intent_response(
    db: Session,
    extracted: ExtractedBookingIntent,
    current_draft: CurrentBookingDraft | None,
    user_message: str,
    today: date | None = None,
    request_id: str | None = None,
) -> BookingIntentResponse:
    trace_id = request_id or uuid4().hex
    request_today = today or date.today()
    followup_response = build_followup_response(
        db,
        user_message=user_message,
        current_draft=current_draft,
    )
    if followup_response is not None:
        log_backend_decision(
            trace_id,
            "build_followup_response",
            "post-AI followup command matched current draft",
        )
        return log_and_return_response(trace_id, followup_response)

    booking_draft = merge_booking_draft(current_draft, extracted)
    booking_draft = normalize_relative_booking_dates(booking_draft, today=request_today)
    log_ai_debug(
        "ai_booking_draft_merge",
        trace_id,
        {
            "draft_before": current_draft,
            "extracted": extracted_intent_debug_payload(extracted),
            "draft_after": booking_draft,
        },
    )
    if extracted.intent == BookingIntent.flexible_availability_search:
        booking_draft = apply_explicit_flexible_criteria(booking_draft, user_message)
    if should_route_to_flexible_availability(extracted, current_draft, booking_draft):
        log_backend_decision(
            trace_id,
            "build_flexible_availability_response",
            "flexible availability intent or flexible draft details after merge",
        )
        return log_and_return_response(
            trace_id,
            build_flexible_availability_response(db, booking_draft),
        )

    if extracted.intent in {BookingIntent.list_services, BookingIntent.service_info}:
        log_backend_decision(
            trace_id,
            "build_service_info_response",
            "service information intent selected",
        )
        return log_and_return_response(
            trace_id,
            build_service_info_response(db, extracted, booking_draft),
        )
    if extracted.intent in {
        BookingIntent.list_masters,
        BookingIntent.master_info,
        BookingIntent.master_service_info,
    }:
        log_backend_decision(
            trace_id,
            "build_master_info_response",
            "master information intent selected",
        )
        return log_and_return_response(trace_id, build_master_info_response(db, extracted))

    missing_fields = get_missing_fields(booking_draft, extracted.intent)
    next_action = get_next_action(booking_draft, extracted.intent, missing_fields)
    availability_result = None

    if should_check_availability(
        booking_draft=booking_draft,
        intent=extracted.intent,
        user_message=user_message,
        missing_fields=missing_fields,
        force_check=time_followup_completed_pending_booking(
            current_draft=current_draft,
            booking_draft=booking_draft,
        ),
    ):
        availability_result = check_booking_draft_availability(db, booking_draft)
        booking_draft = availability_result.booking_draft
        next_action = availability_result.next_action

    backend_message = build_assistant_message(
        booking_draft=booking_draft,
        intent=extracted.intent,
        missing_fields=missing_fields,
        user_message=user_message,
        availability_result=availability_result,
    )
    assistant_message, message_reason = choose_final_assistant_message(
        extracted=extracted,
        backend_message=backend_message,
        missing_fields=missing_fields,
        next_action=next_action,
        availability_result=availability_result,
    )

    response = BookingIntentResponse(
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
    log_backend_decision(
        trace_id,
        "build_booking_intent_response",
        message_reason
        or backend_decision_reason(
            availability_result=availability_result,
            missing_fields=missing_fields,
            next_action=next_action,
        ),
    )
    return log_and_return_response(trace_id, response)


def choose_final_assistant_message(
    *,
    extracted: ExtractedBookingIntent,
    backend_message: str,
    missing_fields: list[str],
    next_action: BookingNextAction,
    availability_result: AvailabilityCheckResult | None,
) -> tuple[str, str]:
    if availability_result is not None:
        return (
            backend_message,
            "backend factual/safety message overrides model text",
        )
    if extracted.intent == BookingIntent.unsupported:
        return (
            backend_message,
            "backend factual/safety message overrides model text",
        )
    if should_prefer_model_conversational_message(
        extracted=extracted,
        missing_fields=missing_fields,
        next_action=next_action,
    ):
        if (
            is_safe_model_conversational_message(extracted.assistant_message)
            and is_model_message_consistent_with_backend_state(
                extracted.assistant_message,
                missing_fields=missing_fields,
                next_action=next_action,
            )
        ):
            return (
                extracted.assistant_message.strip(),
                "used safe model assistant_message for generic conversational response",
            )
        return (
            backend_message,
            "model assistant_message empty, unsafe, or inconsistent with backend state; used backend fallback",
        )
    return (
        backend_message,
        backend_decision_reason(
            availability_result=availability_result,
            missing_fields=missing_fields,
            next_action=next_action,
        ),
    )


def should_prefer_model_conversational_message(
    *,
    extracted: ExtractedBookingIntent,
    missing_fields: list[str],
    next_action: BookingNextAction,
) -> bool:
    if extracted.intent == BookingIntent.unknown:
        return True
    if next_action == BookingNextAction.none:
        return True
    if missing_fields and extracted.intent in {
        BookingIntent.find_booking_slot,
        BookingIntent.ask_booking_question,
        BookingIntent.check_available_masters,
    }:
        return True
    return False


def is_safe_model_conversational_message(message: str | None) -> bool:
    if not message:
        return False

    normalized = " ".join(message.strip().split())
    if not normalized or len(normalized) > 400:
        return False

    lowered = normalized.lower()
    unsafe_fragments = (
        "booked",
        "booking was created",
        "booking is created",
        "confirmed",
        "paid",
        "charged",
        "refunded",
        "create a payment",
        "payment created",
        "refund issued",
        "admin",
        "webhook",
        "token",
        "secret",
        "private data",
        "i changed your booking",
        "i cancelled your booking",
        "slot is available",
        "slot is unavailable",
        "i found availability",
        "available slot",
        "available at",
        "not available",
        "costs €",
        "costs eur",
        "price is",
    )
    if any(fragment in lowered for fragment in unsafe_fragments):
        return False
    if "takes " in lowered and " minute" in lowered:
        return False
    if "€" in normalized:
        return False
    return True


def is_model_message_consistent_with_backend_state(
    message: str | None,
    *,
    missing_fields: list[str],
    next_action: BookingNextAction,
) -> bool:
    if not message:
        return False

    lowered = " ".join(message.lower().split())
    if "date" in missing_fields or next_action == BookingNextAction.ask_date:
        if not any(token in lowered for token in ("date", "day", "when")):
            return False
    if "time" in missing_fields or next_action == BookingNextAction.ask_time:
        if "time" not in lowered and "hour" not in lowered:
            return False
    return True


def time_followup_completed_pending_booking(
    *,
    current_draft: CurrentBookingDraft | None,
    booking_draft: CurrentBookingDraft,
) -> bool:
    if current_draft is None:
        return False

    had_pending_date_and_service = bool(
        current_draft.service_query
        and current_draft.date
        and not current_draft.time
        and not current_draft.time_preference
    )
    has_exact_time = bool(
        booking_draft.time
        and booking_draft.time_preference_type in {"at", "exact"}
    )
    return had_pending_date_and_service and has_exact_time


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
    current_draft: CurrentBookingDraft | None = None,
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
        updated_draft = CurrentBookingDraft.model_validate({
            **(current_draft.model_dump() if current_draft else {}),
            "service_query": service.name,
            "service_id": service.id,
            "last_intent": BookingIntent.service_info.value,
        })
        return BookingIntentResponse(
            intent=BookingIntent.service_info,
            service_query=service.name,
            booking_draft=updated_draft,
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
