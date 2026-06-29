import json
import logging
import time
from typing import Any

from pydantic import ValidationError

from app.ai.client import AIDisabledError, AIProviderError, AIProviderQuotaError
from app.ai.debug import log_ai_debug
from app.ai.prompts import build_booking_intent_prompt
from app.ai.providers.common import (
    TRANSIENT_RETRY_DELAYS_SECONDS,
    describe_provider_error,
    is_quota_provider_error,
    is_transient_provider_error,
    parse_json_object,
)
from app.ai.schemas import BookingIntentExtractionContext, ExtractedBookingIntent
from app.core.config import (
    get_ai_max_output_tokens,
    get_ai_request_timeout_seconds,
    get_ai_temperature,
    get_groq_api_key,
    get_groq_model,
)

logger = logging.getLogger(__name__)


class GroqProvider:
    def __init__(self) -> None:
        api_key = get_groq_api_key()
        if not api_key:
            raise AIDisabledError("Groq API key is not configured")
        self.api_key = api_key
        self.model = get_groq_model()

    def extract_booking_intent(
        self,
        context: BookingIntentExtractionContext,
    ) -> ExtractedBookingIntent:
        try:
            raw_payload = self._generate_json(context)
            return ExtractedBookingIntent.model_validate(raw_payload)
        except (json.JSONDecodeError, ValidationError) as exc:
            logger.warning("[AI] Groq returned invalid booking intent JSON: %s", exc)
            raise AIProviderError("AI provider returned invalid output") from exc
        except AIDisabledError:
            raise
        except AIProviderQuotaError:
            raise
        except AIProviderError:
            raise
        except Exception as exc:
            logger.warning("[AI] Groq booking intent request failed: %s", exc)
            raise AIProviderError("AI provider request failed") from exc

    def _generate_json(self, context: BookingIntentExtractionContext) -> dict[str, object]:
        client = self._build_client()
        completion = self._create_completion_with_retries(
            client=client,
            model=self.model,
            prompt=build_booking_intent_prompt(context),
        )
        choices = getattr(completion, "choices", None)
        if not choices:
            raise AIProviderError("AI provider returned an empty response")

        message = getattr(choices[0], "message", None)
        text = getattr(message, "content", None)
        if not text:
            raise AIProviderError("AI provider returned an empty response")

        if context.request_id:
            log_ai_debug(
                "ai_booking_raw_model_output",
                context.request_id,
                {"raw_output": text},
            )
        return parse_json_object(text)

    def _build_client(self) -> Any:
        try:
            from groq import Groq
        except ImportError as exc:
            raise AIDisabledError("groq is not installed") from exc

        client_kwargs: dict[str, Any] = {"api_key": self.api_key}
        timeout_seconds = get_ai_request_timeout_seconds()
        if timeout_seconds > 0:
            client_kwargs["timeout"] = timeout_seconds

        return Groq(**client_kwargs)

    def _create_completion_with_retries(
        self,
        *,
        client: Any,
        model: str,
        prompt: str,
    ) -> Any:
        max_attempts = len(TRANSIENT_RETRY_DELAYS_SECONDS) + 1

        for attempt_index in range(max_attempts):
            try:
                return client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a careful JSON extraction service. "
                                "Return only one valid JSON object."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=get_ai_temperature(),
                    max_tokens=get_ai_max_output_tokens(),
                    response_format={"type": "json_object"},
                )
            except Exception as exc:
                if is_quota_provider_error(exc):
                    logger.warning(
                        "[AI] Groq quota/rate limit error: %s",
                        describe_provider_error(exc),
                    )
                    raise AIProviderQuotaError("AI provider quota is exhausted") from exc

                is_last_attempt = attempt_index == max_attempts - 1
                if not is_transient_provider_error(exc) or is_last_attempt:
                    raise

                delay_seconds = TRANSIENT_RETRY_DELAYS_SECONDS[attempt_index]
                logger.warning(
                    "[AI] Groq transient error on attempt %s/%s: %s; retrying in %.1fs",
                    attempt_index + 1,
                    max_attempts,
                    describe_provider_error(exc),
                    delay_seconds,
                )
                time.sleep(delay_seconds)

        raise AIProviderError("AI provider request failed")
