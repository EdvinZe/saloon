import logging
import os
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE_URL = "https://api.telegram.org"


def notify_managers(message: str) -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    manager_ids = _get_manager_ids()

    if not token or not manager_ids:
        logger.warning("[NOTIFY] Skipping Telegram notification: token or manager IDs missing")
        return

    for chat_id in manager_ids:
        send_telegram_message(chat_id, message, token=token)


def send_telegram_message(chat_id: int, text: str, *, token: str | None = None) -> None:
    bot_token = token or os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not bot_token:
        logger.warning("[NOTIFY] Skipping Telegram notification: token or manager IDs missing")
        return

    url = f"{TELEGRAM_API_BASE_URL}/bot{bot_token}/sendMessage"
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                url,
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "disable_web_page_preview": True,
                },
            )
            response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning(
            "[NOTIFY] Telegram manager notification failed: chat_id=%s error=%s",
            chat_id,
            _safe_http_error(exc),
        )
        return
    except Exception as exc:
        logger.warning(
            "[NOTIFY] Telegram manager notification failed: chat_id=%s error=%s",
            chat_id,
            exc.__class__.__name__,
        )
        return

    logger.info("[NOTIFY] Telegram manager notification sent: chat_id=%s", chat_id)


def notify_managers_booking_cancelled_today(booking: Any) -> None:
    try:
        if _as_date(getattr(booking, "start_at", None)) != date.today():
            return

        notify_managers(format_booking_cancelled_today_notification(booking))
    except Exception as exc:
        logger.warning(
            "[NOTIFY] Telegram manager notification failed: chat_id=%s error=%s",
            "managers",
            exc.__class__.__name__,
        )


def notify_managers_booking_rescheduled(
    booking: Any,
    old_start_at: datetime,
    old_end_at: datetime,
) -> None:
    try:
        today = date.today()
        if old_start_at.date() != today and _as_date(getattr(booking, "start_at", None)) != today:
            return

        notify_managers(
            format_booking_rescheduled_notification(
                booking,
                old_start_at,
                old_end_at,
            )
        )
    except Exception as exc:
        logger.warning(
            "[NOTIFY] Telegram manager notification failed: chat_id=%s error=%s",
            "managers",
            exc.__class__.__name__,
        )


def format_booking_cancelled_today_notification(booking: Any) -> str:
    return "\n".join(
        [
            "🚫 Booking cancelled today",
            "",
            f"{_format_time_range(booking.start_at, booking.end_at)} — {_service_name(booking)}",
            f"Client: {_client_name(booking)}",
            f"Master: {_master_name(booking)}",
            f"Deposit: {getattr(booking, 'deposit_status', None) or 'unknown'} · {_format_money(booking)}",
            f"Code: {_booking_code(booking)}",
        ]
    )


def format_booking_rescheduled_notification(
    booking: Any,
    old_start_at: datetime,
    old_end_at: datetime,
) -> str:
    return "\n".join(
        [
            "🔁 Booking rescheduled",
            "",
            f"Client: {_client_name(booking)}",
            f"Service: {_service_name(booking)}",
            f"Master: {_master_name(booking)}",
            "",
            "Was:",
            f"{_format_time_range(old_start_at, old_end_at)} · {old_start_at:%Y-%m-%d}",
            "",
            "Now:",
            f"{_format_time_range(booking.start_at, booking.end_at)} · {booking.start_at:%Y-%m-%d}",
            "",
            f"Code: {_booking_code(booking)}",
        ]
    )


def _get_manager_ids() -> list[int]:
    manager_ids = []
    raw_value = os.getenv("TELEGRAM_MANAGER_IDS", "")

    for item in raw_value.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            manager_ids.append(int(item))
        except ValueError:
            logger.warning("[NOTIFY] Skipping invalid Telegram manager ID: %s", item)

    return manager_ids


def _service_name(booking: Any) -> str:
    service = getattr(booking, "service", None)
    name = getattr(service, "name", None)
    return str(name) if name else f"Service #{getattr(booking, 'service_id', '')}"


def _master_name(booking: Any) -> str:
    master = getattr(booking, "master", None)
    first_name = getattr(master, "first_name", None)
    last_name = getattr(master, "last_name", None)
    name = f"{first_name or ''} {last_name or ''}".strip()
    return name or f"Master #{getattr(booking, 'master_id', '')}"


def _client_name(booking: Any) -> str:
    name = (
        f"{getattr(booking, 'customer_first_name', '') or ''} "
        f"{getattr(booking, 'customer_last_name', '') or ''}"
    ).strip()
    return name or "Unknown client"


def _booking_code(booking: Any) -> str:
    return getattr(booking, "booking_code", None) or f"#{getattr(booking, 'id', '')}"


def _format_time_range(start_at: datetime, end_at: datetime) -> str:
    return f"{start_at:%H:%M}–{end_at:%H:%M}"


def _format_money(booking: Any) -> str:
    try:
        amount = Decimal(int(getattr(booking, "deposit_amount_cents", 0))) / Decimal(100)
    except (TypeError, ValueError):
        amount = Decimal(0)

    currency_code = str(getattr(booking, "currency", None) or "EUR").upper()
    symbol = "€" if currency_code == "EUR" else currency_code
    return f"{symbol}{amount:.2f}"


def _as_date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    return None


def _safe_http_error(exc: httpx.HTTPError) -> str:
    if isinstance(exc, httpx.HTTPStatusError):
        return f"HTTPStatusError status_code={exc.response.status_code}"
    return exc.__class__.__name__
