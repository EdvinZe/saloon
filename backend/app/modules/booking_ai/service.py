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
from app.ai.schemas import BookingConversationMessage, CurrentBookingDraft
from app.modules.booking_ai.schemas import BookingIntentResponse
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

    return BookingIntentResponse.model_validate(result.model_dump())
