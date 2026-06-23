import json

from app.ai.client import AIProviderError

TRANSIENT_RETRY_DELAYS_SECONDS = (0.5, 1.0)
TRANSIENT_STATUS_CODES = {500, 502, 503, 504}


def parse_json_object(text: str) -> dict[str, object]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        stripped = text.strip()
        if stripped.startswith("```"):
            stripped = stripped.removeprefix("```json").removeprefix("```").strip()
            stripped = stripped.removesuffix("```").strip()
        payload = json.loads(stripped)

    if not isinstance(payload, dict):
        raise AIProviderError("AI provider returned a non-object response")
    return payload


def get_error_code(exc: Exception) -> int | None:
    code = getattr(exc, "code", None)
    if isinstance(code, int):
        return code

    status_code = getattr(exc, "status_code", None)
    if isinstance(status_code, int):
        return status_code

    response = getattr(exc, "response", None)
    response_status_code = getattr(response, "status_code", None)
    if isinstance(response_status_code, int):
        return response_status_code

    return None


def is_quota_provider_error(exc: Exception) -> bool:
    code = get_error_code(exc)
    status = str(getattr(exc, "status", "")).upper()
    message = str(getattr(exc, "message", "") or exc).lower()
    return (
        code == 429
        or status == "RESOURCE_EXHAUSTED"
        or "quota" in message
        or "resource exhausted" in message
        or "rate limit" in message
        or "rate_limit" in message
    )


def is_transient_provider_error(exc: Exception) -> bool:
    code = get_error_code(exc)
    if isinstance(code, int) and code in TRANSIENT_STATUS_CODES:
        return True

    status = str(getattr(exc, "status", "")).upper()
    if status in {"UNAVAILABLE", "DEADLINE_EXCEEDED"}:
        return True

    message = str(getattr(exc, "message", "") or exc).lower()
    transient_markers = (
        "temporarily unavailable",
        "temporary",
        "high demand",
        "timeout",
        "timed out",
        "connection reset",
        "connection aborted",
    )
    return any(marker in message for marker in transient_markers)


def describe_provider_error(exc: Exception) -> str:
    code = get_error_code(exc)
    status = getattr(exc, "status", None)
    message = str(getattr(exc, "message", "") or exc).replace("\n", " ").strip()
    if len(message) > 140:
        message = f"{message[:137]}..."

    parts = []
    if code is not None:
        parts.append(f"code={code}")
    if status:
        parts.append(f"status={status}")
    if message:
        parts.append(f"reason={message}")

    return ", ".join(parts) or exc.__class__.__name__
