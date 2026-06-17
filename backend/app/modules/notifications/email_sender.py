import logging
from email.utils import formataddr
from typing import Any

import httpx

from app.core.config import get_email_config

logger = logging.getLogger(__name__)

RESEND_EMAILS_URL = "https://api.resend.com/emails"


def send_email(
    to_email: str,
    subject: str,
    text_body: str,
    html_body: str | None = None,
) -> bool:
    config = get_email_config()
    api_key = str(config.get("resend_api_key") or "")
    from_email = str(config.get("from_email") or "").strip()
    from_name = str(config.get("from_name") or "Saloon Booking").strip()

    if not api_key or not from_email:
        logger.warning("[EMAIL] Booking confirmation skipped: Resend config missing")
        return False

    payload: dict[str, Any] = {
        "from": formataddr((from_name, from_email)) if from_name else from_email,
        "to": [to_email],
        "subject": subject,
        "text": text_body,
    }
    if html_body:
        payload["html"] = html_body

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.post(
                RESEND_EMAILS_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        detail = _resend_error_detail(exc.response)
        logger.warning(
            "[EMAIL] Resend API rejected message: to=%s status_code=%s error=%s",
            to_email,
            exc.response.status_code,
            detail,
        )
        raise RuntimeError(
            f"Resend API rejected message: status_code={exc.response.status_code} "
            f"error={detail}"
        ) from exc
    except httpx.HTTPError as exc:
        logger.warning(
            "[EMAIL] Resend API request failed: to=%s error_class=%s error=%r",
            to_email,
            exc.__class__.__name__,
            exc,
        )
        raise

    logger.info("[EMAIL] Resend API accepted message: to=%s", to_email)
    return True


def _resend_error_detail(response: httpx.Response) -> str:
    try:
        data = response.json()
    except ValueError:
        return f"non_json_response:{response.reason_phrase}"

    if isinstance(data, dict):
        message = data.get("message") or data.get("error")
        name = data.get("name")
        if name and message:
            return f"{name}: {message}"
        if message:
            return str(message)

    return "unknown_resend_error"
