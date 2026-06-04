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


def format_report_summary(report: dict, *, scope_label: str) -> str:
    currency = report.get("currency") or "EUR"
    lines = [
        f"Period: {report.get('from_date')} — {report.get('to_date')}",
        f"Scope: {scope_label}",
        "",
        "Bookings:",
        f"Total: {int(report.get('total_bookings') or 0)}",
        f"Confirmed: {int(report.get('confirmed_count') or 0)}",
        f"Completed: {int(report.get('completed_count') or 0)}",
        f"No-show: {int(report.get('no_show_count') or 0)}",
        f"Cancelled: {int(report.get('cancelled_count') or 0)}",
        "",
        "Deposits:",
        f"Paid: {_format_money(report.get('paid_deposits_cents'), currency)}",
        f"Refunded: {_format_money(report.get('refunded_deposits_cents'), currency)}",
        f"Net: {_format_money(report.get('net_deposits_cents'), currency)}",
    ]

    if int(report.get("total_bookings") or 0) == 0:
        lines.extend(["", "No bookings found for this period."])

    by_master = report.get("by_master")
    if scope_label == "All masters" and isinstance(by_master, list) and by_master:
        lines.extend(["", "By master:"])
        for row in by_master[:6]:
            if not isinstance(row, dict):
                continue
            name = row.get("master_name") or f"Master #{row.get('master_id')}"
            bookings = int(row.get("total_bookings") or 0)
            net = _format_money(row.get("net_deposits_cents"), currency)
            lines.append(f"{name} — {bookings} bookings · net {net}")

    by_service = report.get("by_service")
    if isinstance(by_service, list) and by_service:
        lines.extend(["", "Top services:"])
        sorted_services = sorted(
            [row for row in by_service if isinstance(row, dict)],
            key=lambda row: int(row.get("total_bookings") or 0),
            reverse=True,
        )
        for row in sorted_services[:3]:
            name = row.get("service_name") or f"Service #{row.get('service_id')}"
            bookings = int(row.get("total_bookings") or 0)
            net = _format_money(row.get("net_deposits_cents"), currency)
            lines.append(f"{name} — {bookings} bookings · net {net}")

    return "\n".join(lines)
