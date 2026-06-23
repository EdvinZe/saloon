import json
import logging
from typing import Any

from pydantic import ValidationError

from app.ai.client import AIDisabledError, AIProviderError
from app.ai.prompts import build_booking_intent_prompt
from app.ai.schemas import BookingIntentExtractionContext, ExtractedBookingIntent
from app.core.config import (
    get_ai_max_output_tokens,
    get_ai_model,
    get_ai_request_timeout_seconds,
    get_ai_temperature,
    get_gemini_api_key,
)

logger = logging.getLogger(__name__)


class GeminiProvider:
    def __init__(self) -> None:
        api_key = get_gemini_api_key()
        if not api_key:
            raise AIDisabledError("Gemini API key is not configured")
        self.api_key = api_key
        self.model = get_ai_model()

    def extract_booking_intent(
        self,
        context: BookingIntentExtractionContext,
    ) -> ExtractedBookingIntent:
        try:
            raw_payload = self._generate_json(context)
            return ExtractedBookingIntent.model_validate(raw_payload)
        except (json.JSONDecodeError, ValidationError) as exc:
            logger.warning("[AI] Gemini returned invalid booking intent JSON: %s", exc)
            raise AIProviderError("AI provider returned invalid output") from exc
        except AIDisabledError:
            raise
        except AIProviderError:
            raise
        except Exception as exc:
            logger.warning("[AI] Gemini booking intent request failed: %s", exc)
            raise AIProviderError("AI provider request failed") from exc

    def _generate_json(self, context: BookingIntentExtractionContext) -> dict[str, Any]:
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise AIDisabledError("google-genai is not installed") from exc

        client_kwargs: dict[str, Any] = {"api_key": self.api_key}
        timeout_seconds = get_ai_request_timeout_seconds()
        if timeout_seconds > 0:
            client_kwargs["http_options"] = types.HttpOptions(
                timeout=timeout_seconds * 1000,
            )

        client = genai.Client(**client_kwargs)
        config = types.GenerateContentConfig(
            temperature=get_ai_temperature(),
            max_output_tokens=get_ai_max_output_tokens(),
            response_mime_type="application/json",
            response_schema=ExtractedBookingIntent,
        )
        response = client.models.generate_content(
            model=self.model,
            contents=build_booking_intent_prompt(context),
            config=config,
        )
        text = getattr(response, "text", None)
        if not text:
            raise AIProviderError("AI provider returned an empty response")
        payload = json.loads(text)
        if not isinstance(payload, dict):
            raise AIProviderError("AI provider returned a non-object response")
        return payload
