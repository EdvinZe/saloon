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
    manager_ids = get_manager_chat_ids()

    if not manager_ids:
        return

    for chat_id in manager_ids:
        send_telegram_message(chat_id, message)


def send_telegram_message(chat_id: int, text: str) -> bool:
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not bot_token:
        logger.warning("[NOTIFY] Telegram notification skipped: token missing")
        return False

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
            "[NOTIFY] Telegram notification failed: chat_id=%s error=%s",
            chat_id,
            _safe_http_error(exc),
        )
        return False
    except Exception as exc:
        logger.warning(
            "[NOTIFY] Telegram notification failed: chat_id=%s error=%s",
            chat_id,
            exc.__class__.__name__,
        )
        return False

    return True


def notify_new_same_day_booking(booking: Any) -> None:
    try:
        logger.info(
            "[NOTIFY] Same-day booking notification requested: booking_id=%s booking_code=%s",
            getattr(booking, "id", None),
            _booking_code(booking),
        )

        if _as_date(getattr(booking, "start_at", None)) != date.today():
            logger.info(
                "[NOTIFY] Same-day booking notification skipped: booking_id=%s reason=%s",
                getattr(booking, "id", None),
                "not_today",
            )
            return

        notify_managers_new_booking_today(booking)
        notify_barbers_new_booking_today(booking)
    except Exception as exc:
        logger.warning(
            "[NOTIFY] Telegram notification failed: chat_id=%s error=%s",
            "same_day_booking",
            exc.__class__.__name__,
        )


def notify_managers_new_booking_today(booking: Any) -> None:
    manager_chat_ids = get_manager_chat_ids()
    if not manager_chat_ids:
        logger.info(
            "[NOTIFY] Same-day booking notification skipped: booking_id=%s reason=%s",
            getattr(booking, "id", None),
            "manager_chat_ids_missing",
        )
        return

    message = format_manager_new_booking_today_message(booking)
    for chat_id in manager_chat_ids:
        if send_telegram_message(chat_id, message):
            logger.info(
                "[NOTIFY] Manager new booking notification sent: chat_id=%s booking_id=%s",
                chat_id,
                getattr(booking, "id", None),
            )


def notify_barbers_new_booking_today(booking: Any) -> None:
    master_id = getattr(booking, "master_id", None)
    if master_id is None:
        logger.info(
            "[NOTIFY] Same-day booking notification skipped: booking_id=%s reason=%s",
            getattr(booking, "id", None),
            "master_id_missing",
        )
        return

    barber_chat_ids = get_barber_chat_ids_for_master(int(master_id))
    if not barber_chat_ids:
        logger.info(
            "[NOTIFY] Same-day booking notification skipped: booking_id=%s reason=%s",
            getattr(booking, "id", None),
            "barber_chat_ids_missing",
        )
        return

    message = format_barber_new_booking_today_message(booking)
    for chat_id in barber_chat_ids:
        if send_telegram_message(chat_id, message):
            logger.info(
                "[NOTIFY] Barber new booking notification sent: chat_id=%s booking_id=%s master_id=%s",
                chat_id,
                getattr(booking, "id", None),
                master_id,
            )


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


def format_manager_new_booking_today_message(booking: Any) -> str:
    return "\n".join(
        [
            "🆕 New booking for today",
            "",
            f"{booking.start_at:%H:%M} — {_service_name(booking)}",
            f"Master: {_master_name(booking)}",
            f"Client: {_client_name(booking)}",
            f"Deposit: {getattr(booking, 'deposit_status', None) or 'unknown'} · {_format_money(booking)}",
        ]
    )


def format_barber_new_booking_today_message(booking: Any) -> str:
    lines = [
        "🆕 New booking for you today",
        "",
        f"{_format_time_range(booking.start_at, booking.end_at)} — {_service_name(booking)}",
        f"Client: {_client_name(booking)}",
        f"Phone: {_client_phone(booking)}",
        f"Deposit: {getattr(booking, 'deposit_status', None) or 'unknown'} · {_format_money(booking)}",
    ]

    remaining_amount_cents = getattr(booking, "remaining_amount_cents", None)
    if remaining_amount_cents is not None:
        lines.append(f"Remaining to collect: {_format_cents(remaining_amount_cents, booking)}")

    payment_method = getattr(booking, "payment_method", None)
    if payment_method:
        lines.append(f"Payment method: {payment_method}")

    lines.append(f"Code: {_booking_code(booking)}")
    return "\n".join(lines)


def parse_telegram_manager_ids(raw: str) -> list[int]:
    manager_ids: list[int] = []

    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            chat_id = int(item)
        except ValueError:
            logger.warning("[NOTIFY] Skipping invalid Telegram manager ID: %s", item)
            continue
        if chat_id not in manager_ids:
            manager_ids.append(chat_id)

    return manager_ids


def parse_telegram_barber_master_map(raw: str) -> dict[int, int]:
    barber_master_map: dict[int, int] = {}

    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue

        try:
            raw_chat_id, raw_master_id = item.split(":", maxsplit=1)
        except ValueError:
            logger.warning("[NOTIFY] Skipping invalid Telegram barber map value: %s", item)
            continue

        try:
            barber_master_map[int(raw_chat_id.strip())] = int(raw_master_id.strip())
        except ValueError:
            logger.warning("[NOTIFY] Skipping invalid Telegram barber map value: %s", item)

    return barber_master_map


def get_manager_chat_ids() -> list[int]:
    return parse_telegram_manager_ids(os.getenv("TELEGRAM_MANAGER_IDS", ""))


def get_barber_chat_ids_for_master(master_id: int) -> list[int]:
    barber_master_map = parse_telegram_barber_master_map(
        os.getenv("TELEGRAM_BARBER_MASTER_MAP", "")
    )
    return [
        chat_id
        for chat_id, mapped_master_id in barber_master_map.items()
        if mapped_master_id == master_id
    ]


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


def _client_phone(booking: Any) -> str:
    return getattr(booking, "customer_phone", None) or "Not provided"


def _booking_code(booking: Any) -> str:
    return getattr(booking, "booking_code", None) or f"#{getattr(booking, 'id', '')}"


def _format_time_range(start_at: datetime, end_at: datetime) -> str:
    return f"{start_at:%H:%M}–{end_at:%H:%M}"


def _format_money(booking: Any) -> str:
    return _format_cents(getattr(booking, "deposit_amount_cents", 0), booking)


def _format_cents(amount_cents: Any, booking: Any) -> str:
    try:
        amount = Decimal(int(amount_cents)) / Decimal(100)
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
