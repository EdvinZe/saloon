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


def format_now_message(context: dict) -> str:
    role = context.get("role")
    now = context.get("now")
    now_text = now.strftime("%H:%M") if isinstance(now, datetime) else ""

    if role == "barber":
        return _format_barber_now_message(context, now_text)
    return _format_manager_now_message(context, now_text)


def _format_manager_now_message(context: dict, now_text: str) -> str:
    lines = ["🟢 Now in salon", f"Time: {now_text}"]
    masters = context.get("masters")

    if isinstance(masters, list) and masters:
        for master in masters:
            if not isinstance(master, dict):
                continue
            lines.extend(["", str(master.get("name") or f"Master #{master.get('id')}")])
            lines.append(f"Working: {_format_shift_range(master)}")
            lines.extend(_format_now_booking_block(master))
        return "\n".join(lines)

    lines.extend(["", "No masters are currently working."])
    upcoming_bookings = context.get("upcoming_bookings")
    if isinstance(upcoming_bookings, list) and upcoming_bookings:
        lines.extend(["", "Upcoming reservations today:"])
        for booking in upcoming_bookings:
            if not isinstance(booking, dict):
                continue
            master = booking.get("master_name") or f"Master #{booking.get('master_id')}"
            lines.append(f"{_format_booking_line(booking)} — {master}")

    return "\n".join(lines)


def _format_barber_now_message(context: dict, now_text: str) -> str:
    lines = ["🟢 Your status now", f"Time: {now_text}"]
    masters = context.get("masters")

    if isinstance(masters, list) and masters:
        master = masters[0]
        if isinstance(master, dict):
            lines.extend(["", f"Working: {_format_shift_range(master)}"])
            lines.extend(_format_now_booking_block(master))
            return "\n".join(lines)

    lines.extend(["", "You are not currently working."])
    current_booking = context.get("current_booking")
    next_booking = context.get("next_booking")
    if isinstance(current_booking, dict):
        lines.extend(["", "Current booking:"])
        lines.extend(_format_booking_details(current_booking))
    elif isinstance(next_booking, dict):
        lines.extend(["", "No current booking.", "Next today:"])
        lines.extend(_format_booking_details(next_booking))
    else:
        lines.extend(["", "No reservations today."])

    return "\n".join(lines)


def _format_now_booking_block(master: dict) -> list[str]:
    current_booking = master.get("current_booking")
    next_booking = master.get("next_booking")

    if isinstance(current_booking, dict):
        return ["Current booking:", *_format_booking_details(current_booking)]
    if isinstance(next_booking, dict):
        return ["No current booking.", "Next today:", *_format_booking_details(next_booking)]
    return ["No reservations today."]


def _format_booking_details(booking: dict) -> list[str]:
    lines = [_format_booking_line(booking)]
    client = _full_name(
        booking.get("customer_first_name"),
        booking.get("customer_last_name"),
    )
    lines.append(f"Client: {client}")

    deposit = booking.get("deposit_status")
    if deposit:
        lines.append(
            f"Deposit: {deposit} · "
            f"{_format_money(booking.get('deposit_amount_cents'), booking.get('currency'))}"
        )

    code = booking.get("booking_code")
    if code:
        lines.append(f"Code: {code}")

    return lines


def _format_booking_line(booking: dict) -> str:
    service = booking.get("service_name") or f"Service #{booking.get('service_id')}"
    return f"{_format_time(booking.get('start_at'))}–{_format_time(booking.get('end_at'))} — {service}"


def _format_shift_range(master: dict) -> str:
    return f"{master.get('start_time') or '?'}–{master.get('end_time') or '?'}"


def format_report_summary(
    report: dict,
    title: str | None = None,
    *,
    scope_label: str = "All masters",
) -> str:
    currency = report.get("currency") or "EUR"
    lines = []
    if title:
        lines.append(title)

    lines.extend(
        [
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
    )

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

    return "\n".join(lines)
