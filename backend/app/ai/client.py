from datetime import date

from app.ai.schemas import (
    BookingConversationMessage,
    BookingIntentExtractionContext,
    CurrentBookingDraft,
    ExtractedBookingIntent,
)
from app.core.config import (
    get_ai_daily_request_limit,
    get_ai_provider,
    is_ai_enabled,
)


class AIError(Exception):
    """Base class for internal AI failures."""


class AIDisabledError(AIError):
    """Raised when AI is disabled or not configured."""


class AIProviderError(AIError):
    """Raised when the provider fails or returns invalid output."""


class AIProviderQuotaError(AIProviderError):
    """Raised when the upstream AI provider quota is exhausted."""


class AIRateLimitError(AIError):
    """Raised when the lightweight daily AI limit is exhausted."""


class AIClient:
    def __init__(self) -> None:
        self._limit_day: date | None = None
        self._daily_count = 0

    def extract_booking_intent(
        self,
        *,
        user_message: str,
        today: date,
        service_names: list[str],
        conversation_messages: list[BookingConversationMessage] | None = None,
        current_booking_draft: CurrentBookingDraft | None = None,
    ) -> ExtractedBookingIntent:
        if not is_ai_enabled():
            raise AIDisabledError("AI is disabled")

        self._check_daily_limit(today)
        provider = self._build_provider()
        context = BookingIntentExtractionContext(
            today=today,
            service_names=service_names,
            user_message=user_message,
            conversation_messages=conversation_messages or [],
            current_booking_draft=current_booking_draft,
        )
        result = provider.extract_booking_intent(context)
        self._daily_count += 1
        return result

    def _build_provider(self):
        provider_name = get_ai_provider()
        if provider_name == "gemini":
            from app.ai.providers.gemini_provider import GeminiProvider

            return GeminiProvider()
        if provider_name == "groq":
            from app.ai.providers.groq_provider import GroqProvider

            return GroqProvider()
        raise AIDisabledError(f"Unsupported AI provider: {provider_name}")

    def _check_daily_limit(self, today: date) -> None:
        limit = get_ai_daily_request_limit()
        if limit <= 0:
            raise AIRateLimitError("AI daily request limit is exhausted")

        if self._limit_day != today:
            self._limit_day = today
            self._daily_count = 0

        if self._daily_count >= limit:
            raise AIRateLimitError("AI daily request limit is exhausted")


ai_client = AIClient()
