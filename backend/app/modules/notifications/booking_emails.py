import logging
from typing import Any
from urllib.parse import urlencode

from app.core.config import get_public_frontend_url
from app.modules.notifications.email_sender import send_email
from app.modules.notifications.email_templates import (
    format_date,
    format_money,
    format_time_range,
    render_booking_confirmation_html,
    render_booking_confirmation_text,
)

logger = logging.getLogger(__name__)


def send_booking_confirmation_email(booking: Any) -> None:
    booking_id = getattr(booking, "id", None)
    to_email = str(getattr(booking, "customer_email", "") or "").strip()
    if not to_email:
        logger.info(
            "[EMAIL] Booking confirmation skipped: client email missing booking_id=%s",
            booking_id,
        )
        return

    manage_token = str(getattr(booking, "manage_token", "") or "").strip()
    if not manage_token:
        logger.warning(
            "[EMAIL] Booking confirmation skipped: manage token missing booking_id=%s",
            booking_id,
        )
        return

    try:
        client_name = _client_name(booking)
        service_name = _service_name(booking)
        master_name = _master_name(booking)
        start_at = getattr(booking, "start_at", None)
        end_at = getattr(booking, "end_at", None)
        deposit_text = _deposit_text(booking)
        manage_link = _manage_link(manage_token)

        text_body = render_booking_confirmation_text(
            client_name=client_name,
            service_name=service_name,
            master_name=master_name,
            date_text=format_date(start_at),
            time_range=format_time_range(start_at, end_at),
            deposit_text=deposit_text,
            manage_link=manage_link,
        )
        html_body = render_booking_confirmation_html(
            client_name=client_name,
            service_name=service_name,
            master_name=master_name,
            date_text=format_date(start_at),
            time_range=format_time_range(start_at, end_at),
            deposit_text=deposit_text,
            manage_link=manage_link,
        )
        sent = send_email(
            to_email=to_email,
            subject="Your booking is confirmed",
            text_body=text_body,
            html_body=html_body,
        )
    except Exception as exc:
        logger.error(
            "[EMAIL] Booking confirmation failed: booking_id=%s error=%s",
            booking_id,
            exc.__class__.__name__,
        )
        return

    if sent:
        logger.info(
            "[EMAIL] Booking confirmation sent: booking_id=%s to=%s",
            booking_id,
            to_email,
        )


def _manage_link(manage_token: str) -> str:
    return f"{get_public_frontend_url()}/booking/manage?{urlencode({'token': manage_token})}"


def _client_name(booking: Any) -> str | None:
    name = " ".join(
        part
        for part in [
            str(getattr(booking, "customer_first_name", "") or "").strip(),
            str(getattr(booking, "customer_last_name", "") or "").strip(),
        ]
        if part
    )
    return name or None


def _service_name(booking: Any) -> str:
    service = getattr(booking, "service", None)
    name = str(getattr(service, "name", "") or "").strip()
    if name:
        return name
    return f"Service #{getattr(booking, 'service_id', '')}"


def _master_name(booking: Any) -> str:
    master = getattr(booking, "master", None)
    name = " ".join(
        part
        for part in [
            str(getattr(master, "first_name", "") or "").strip(),
            str(getattr(master, "last_name", "") or "").strip(),
        ]
        if part
    )
    if name:
        return name
    return f"Master #{getattr(booking, 'master_id', '')}"


def _deposit_text(booking: Any) -> str | None:
    status = str(getattr(booking, "deposit_status", "") or "").strip()
    amount = format_money(
        getattr(booking, "deposit_amount_cents", None),
        getattr(booking, "currency", None),
    )
    if status and amount:
        return f"{status} · {amount}"
    if status:
        return status
    if amount:
        return amount
    return None
