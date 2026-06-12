from datetime import datetime
from decimal import Decimal
from html import escape


def format_date(value: datetime | None) -> str:
    if value is None:
        return "Not available"
    return f"{value.day} {value:%B %Y}"


def format_time_range(start_at: datetime | None, end_at: datetime | None) -> str:
    if start_at is None and end_at is None:
        return "Not available"
    if start_at is None:
        return end_at.strftime("%H:%M") if end_at else "Not available"
    if end_at is None:
        return start_at.strftime("%H:%M")
    return f"{start_at:%H:%M}–{end_at:%H:%M}"


def format_money(cents: int | None, currency: str | None) -> str | None:
    if cents is None:
        return None
    amount = Decimal(int(cents)) / Decimal(100)
    currency_code = str(currency or "EUR").upper()
    symbol = "€" if currency_code == "EUR" else currency_code
    return f"{symbol}{amount:.2f}"


def render_booking_confirmation_text(
    *,
    client_name: str | None,
    service_name: str,
    master_name: str,
    date_text: str,
    time_range: str,
    deposit_text: str | None,
    manage_link: str,
) -> str:
    greeting = f"Hi {client_name}," if client_name else "Hi,"
    lines = [
        greeting,
        "",
        "Your booking is confirmed.",
        "",
        f"Service: {service_name}",
        f"Master: {master_name}",
        f"Date: {date_text}",
        f"Time: {time_range}",
    ]
    if deposit_text:
        lines.append(f"Deposit: {deposit_text}")

    lines.extend(
        [
            "",
            "You can view, reschedule, or cancel your booking using this link:",
            manage_link,
            "",
            "Please keep this email for your records.",
        ]
    )
    return "\n".join(lines)


def render_booking_confirmation_html(
    *,
    client_name: str | None,
    service_name: str,
    master_name: str,
    date_text: str,
    time_range: str,
    deposit_text: str | None,
    manage_link: str,
) -> str:
    greeting = f"Hi {escape(client_name)}," if client_name else "Hi,"
    deposit_item = (
        f"\n  <li><strong>Deposit:</strong> {escape(deposit_text)}</li>"
        if deposit_text
        else ""
    )

    return "\n".join(
        [
            "<h2>Your booking is confirmed</h2>",
            "",
            f"<p>{greeting}</p>",
            "",
            "<p>Your booking is confirmed.</p>",
            "",
            "<ul>",
            f"  <li><strong>Service:</strong> {escape(service_name)}</li>",
            f"  <li><strong>Master:</strong> {escape(master_name)}</li>",
            f"  <li><strong>Date:</strong> {escape(date_text)}</li>",
            f"  <li><strong>Time:</strong> {escape(time_range)}</li>{deposit_item}",
            "</ul>",
            "",
            f'<p><a href="{escape(manage_link, quote=True)}">Manage your booking</a></p>',
            "",
            "<p>You can use this link to view, reschedule, or cancel your appointment.</p>",
        ]
    )
