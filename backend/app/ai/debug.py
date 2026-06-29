import logging
import re
from enum import Enum
from typing import Any

from pydantic import BaseModel

from app.core.config import is_ai_debug_enabled

logger = logging.getLogger("app.ai.booking_debug")

_EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_PHONE_PATTERN = re.compile(r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)")
_NAME_PHRASE_PATTERN = re.compile(
    r"\b(my name is|name is|i am|i'm)\s+[A-Z][A-Za-z.'-]*(?:\s+[A-Z][A-Za-z.'-]*){0,2}",
    re.IGNORECASE,
)
_SENSITIVE_KEYS = {
    "api_key",
    "authorization",
    "customer_email",
    "customer_name",
    "customer_phone",
    "email",
    "manage_token",
    "password",
    "phone",
    "secret",
    "stripe_secret",
    "token",
}
_TRACE_SEPARATOR = "─────────────────────────────────────"
_RAW_OUTPUT_MAX_CHARS = 3000
_DRAFT_FIELDS = (
    ("service", "service_query"),
    ("service_id", "service_id"),
    ("master", "master_query"),
    ("master_id", "master_id"),
    ("master_name", "master_name"),
    ("date", "date"),
    ("start_date", "start_date"),
    ("end_date", "end_date"),
    ("time", "time"),
    ("end_time", "end_time"),
    ("time_preference", "time_preference"),
    ("time_preference_type", "time_preference_type"),
    ("weekdays", "weekdays"),
    ("last_intent", "last_intent"),
    ("shown_option_count", "shown_option_count"),
)


def ai_debug_enabled() -> bool:
    return is_ai_debug_enabled()


def log_ai_debug(event: str, request_id: str, payload: dict[str, Any] | None = None) -> None:
    if not ai_debug_enabled():
        return

    safe_payload = mask_sensitive_data(payload or {})
    logger.info("%s", "\n".join(_format_trace_lines(event, request_id, safe_payload)))


def mask_sensitive_data(value: Any) -> Any:
    plain_value = _to_plain_value(value)
    if isinstance(plain_value, dict):
        return {
            key: "<redacted>" if _is_sensitive_key(str(key)) else mask_sensitive_data(item)
            for key, item in plain_value.items()
        }
    if isinstance(plain_value, list):
        return [mask_sensitive_data(item) for item in plain_value]
    if isinstance(plain_value, str):
        return _mask_text(plain_value)
    return plain_value


def _to_plain_value(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {
            _to_plain_value(key): _to_plain_value(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple, set)):
        return [_to_plain_value(item) for item in value]
    return value


def _mask_text(value: str) -> str:
    masked = _EMAIL_PATTERN.sub("<redacted-email>", value)
    masked = _PHONE_PATTERN.sub("<redacted-phone>", masked)
    return _NAME_PHRASE_PATTERN.sub(lambda match: f"{match.group(1)} <redacted-name>", masked)


def _is_sensitive_key(key: str) -> bool:
    normalized = key.strip().lower()
    return normalized in _SENSITIVE_KEYS or normalized.endswith("_secret") or normalized.endswith("_token")


def _format_trace_lines(event: str, request_id: str, payload: dict[str, Any]) -> list[str]:
    prefix = _prefix(request_id)
    if event == "ai_booking_request":
        return [
            f"{prefix} {_TRACE_SEPARATOR}",
            f"{prefix} USER MESSAGE",
            f"{prefix}   text: {_quote(payload.get('message'))}",
            f"{prefix}   conversation_messages_count: {_display_value(payload.get('conversation_messages_count'))}",
            f"{prefix}   incoming_draft:",
            *_draft_lines(prefix, payload.get("current_booking_draft")),
        ]
    if event == "ai_booking_prompt_context":
        return [
            f"{prefix} MODEL CONTEXT",
            f"{prefix}   today: {_display_value(payload.get('today'))}",
            f"{prefix}   services: {_display_list(payload.get('services'))}",
            f"{prefix}   masters: {_display_list(payload.get('masters'))}",
            f"{prefix}   recent_conversation_lines_count: "
            f"{_display_value(payload.get('recent_conversation_lines_count'))}",
            f"{prefix}   draft:",
            *_draft_lines(prefix, payload.get("draft_context")),
        ]
    if event == "ai_booking_raw_model_output":
        raw_output = str(payload.get("raw_output") or "-")
        return [
            f"{prefix} RAW MODEL OUTPUT",
            *[
                f"{prefix}   {line}"
                for line in _truncate(raw_output, _RAW_OUTPUT_MAX_CHARS).splitlines()
            ],
        ]
    if event == "ai_booking_parsed_intent":
        return [
            f"{prefix} PARSED MODEL OUTPUT",
            f"{prefix}   intent: {_display_value(payload.get('intent'))}",
            f"{prefix}   service_query: {_display_value(payload.get('service_query'))}",
            f"{prefix}   master_query: {_display_value(payload.get('master_query'))}",
            f"{prefix}   date: {_display_value(payload.get('date'))}",
            f"{prefix}   time: {_display_value(payload.get('time'))}",
            f"{prefix}   time_preference: {_display_value(payload.get('time_preference'))}",
            f"{prefix}   time_preference_type: {_display_value(payload.get('time_preference_type'))}",
            f"{prefix}   missing_fields: {_display_list(payload.get('missing_fields'), empty='[]')}",
            f"{prefix}   assistant_message: {_quote(payload.get('assistant_message'))}",
        ]
    if event == "ai_booking_draft_merge":
        return [
            f"{prefix} DRAFT MERGE",
            f"{prefix}   before:",
            *_draft_lines(prefix, payload.get("draft_before")),
            f"{prefix}   extracted:",
            *_extracted_lines(prefix, payload.get("extracted")),
            f"{prefix}   after:",
            *_draft_lines(prefix, payload.get("draft_after")),
        ]
    if event == "ai_booking_backend_decision":
        model_call = payload.get("model_call")
        if model_call is None and payload.get("handler") == "build_local_pre_ai_response":
            model_call = "skipped"
        lines = [
            f"{prefix} BACKEND DECISION",
            f"{prefix}   handler: {_display_value(payload.get('handler'))}",
            f"{prefix}   reason: {_display_value(payload.get('reason'))}",
        ]
        if model_call is not None:
            lines.append(f"{prefix}   model_call: {_display_value(model_call)}")
        return lines
    if event == "ai_booking_response":
        return [
            f"{prefix} FINAL RESPONSE",
            f"{prefix}   intent: {_display_value(payload.get('intent'))}",
            f"{prefix}   next_action: {_display_value(payload.get('next_action'))}",
            f"{prefix}   missing_fields: {_display_list(payload.get('missing_fields'), empty='[]')}",
            f"{prefix}   message: {_quote(payload.get('assistant_message'))}",
            f"{prefix}   actions_count: {_display_value(payload.get('actions_count'))}",
            f"{prefix}   available_options_count: {_display_value(payload.get('available_options_count'))}",
            f"{prefix}   outgoing_draft:",
            *_draft_lines(prefix, payload.get("booking_draft")),
            f"{prefix} END TRACE",
        ]
    return [
        f"{prefix} {event}",
        *[f"{prefix}   {key}: {_display_value(value)}" for key, value in payload.items()],
    ]


def _prefix(request_id: str) -> str:
    return f"[AI BOOKING][{request_id[:8]}]"


def _draft_lines(prefix: str, draft: Any) -> list[str]:
    payload = draft if isinstance(draft, dict) else {}
    lines = [
        f"{prefix}     {label}: {_display_value(payload.get(key))}"
        for label, key in _DRAFT_FIELDS
    ]
    last_options = payload.get("last_available_options")
    if isinstance(last_options, list):
        lines.append(f"{prefix}     available_options_count: {len(last_options)}")
    return lines


def _extracted_lines(prefix: str, extracted: Any) -> list[str]:
    payload = extracted if isinstance(extracted, dict) else {}
    return [
        f"{prefix}     intent: {_display_value(payload.get('intent'))}",
        f"{prefix}     service_query: {_display_value(payload.get('service_query'))}",
        f"{prefix}     master_query: {_display_value(payload.get('master_query'))}",
        f"{prefix}     date: {_display_value(payload.get('date'))}",
        f"{prefix}     time: {_display_value(payload.get('time'))}",
        f"{prefix}     time_preference: {_display_value(payload.get('time_preference'))}",
        f"{prefix}     time_preference_type: {_display_value(payload.get('time_preference_type'))}",
        f"{prefix}     missing_fields: {_display_list(payload.get('missing_fields'), empty='[]')}",
    ]


def _display_value(value: Any) -> str:
    if value in (None, "", [], {}):
        return "-"
    if isinstance(value, list):
        return _display_list(value)
    return str(value)


def _display_list(value: Any, *, empty: str = "-") -> str:
    if not value:
        return empty
    if isinstance(value, list):
        return ", ".join(str(item) for item in value) or empty
    return str(value)


def _quote(value: Any) -> str:
    if value in (None, ""):
        return "-"
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _truncate(value: str, max_chars: int) -> str:
    if len(value) <= max_chars:
        return value
    return f"{value[:max_chars]}... <truncated {len(value) - max_chars} chars>"
