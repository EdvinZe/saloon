from datetime import datetime
from decimal import Decimal
from typing import Any


def _parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _format_time(value: Any) -> str:
    parsed = _parse_datetime(value)
    if parsed is None:
        return str(value or "")
    return parsed.strftime("%H:%M")


def _format_money(cents: Any, currency: Any) -> str:
    try:
        amount = Decimal(int(cents)) / Decimal(100)
    except (TypeError, ValueError):
        amount = Decimal(0)

    currency_code = str(currency or "eur").upper()
    symbol = "€" if currency_code == "EUR" else currency_code
    return f"{symbol}{amount:.2f}"


def _full_name(first_name: Any, last_name: Any) -> str:
    name = f"{first_name or ''} {last_name or ''}".strip()
    return name or "Unknown client"


def format_bookings_header(label: str, date: str) -> str:
    return f"{label} ({date})"


def format_booking_message(booking: dict) -> str:
    # TODO: Later enrich admin bookings response with service_name/master_name if needed.
    service = booking.get("service_name") or f"Service #{booking.get('service_id')}"
    master = booking.get("master_name") or f"Master #{booking.get('master_id')}"
    client = _full_name(
        booking.get("customer_first_name"),
        booking.get("customer_last_name"),
    )
    deposit = booking.get("deposit_status") or "unknown"
    amount = _format_money(
        booking.get("deposit_amount_cents"),
        booking.get("currency"),
    )
    status = booking.get("status") or "unknown"
    code = booking.get("booking_code") or f"#{booking.get('id')}"
    start_time = _format_time(booking.get("start_at"))
    end_time = _format_time(booking.get("end_at"))

    return "\n".join(
        [
            f"{start_time}–{end_time} — {service}",
            f"Client: {client}",
            f"Master: {master}",
            f"Deposit: {deposit} · {amount}",
            f"Status: {status}",
            f"Code: {code}",
        ]
    )
