import logging
from dataclasses import dataclass
from typing import Any

import stripe
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import require_stripe_secret_key
from app.modules.bookings.models import Booking
from app.modules.bookings.schemas import BookingCreate
from app.modules.bookings.service import (
    create_confirmed_booking,
    get_booking_by_payment_intent,
)
from app.modules.notifications.booking_emails import send_booking_confirmation_email

logger = logging.getLogger(__name__)

REQUIRED_PAYMENT_INTENT_METADATA = {
    "service_id",
    "master_id",
    "date",
    "time",
    "customer_first_name",
    "customer_last_name",
    "customer_phone",
    "customer_email",
    "deposit_amount_cents",
    "currency",
}


@dataclass(frozen=True)
class PaymentIntentBookingResult:
    status: str
    message: str
    booking: Booking | None = None
    created: bool = False


class PaymentIntentBookingCreationError(Exception):
    """Raised when a paid PaymentIntent cannot safely create a booking."""


def confirm_paid_payment_intent_and_create_booking(
    db: Session,
    payment_intent_id: str,
    *,
    payment_intent: Any | None = None,
) -> PaymentIntentBookingResult:
    cleaned_payment_intent_id = payment_intent_id.strip()
    if not cleaned_payment_intent_id:
        return PaymentIntentBookingResult(
            status="not_found",
            message="Payment intent is missing",
        )

    existing_booking = get_booking_by_payment_intent(db, cleaned_payment_intent_id)
    if existing_booking is not None:
        return PaymentIntentBookingResult(
            status="confirmed",
            message="Booking confirmed",
            booking=existing_booking,
            created=False,
        )

    try:
        payment_intent = payment_intent or retrieve_payment_intent(cleaned_payment_intent_id)
    except stripe.error.InvalidRequestError:
        logger.warning(
            "[PAYMENTS] PaymentIntent lookup failed: payment_intent_id=%s reason=%s",
            cleaned_payment_intent_id,
            "not_found",
        )
        return PaymentIntentBookingResult(
            status="not_found",
            message="Payment intent was not found",
        )
    except stripe.error.StripeError as exc:
        logger.warning(
            "[PAYMENTS] PaymentIntent lookup failed: payment_intent_id=%s error=%s",
            cleaned_payment_intent_id,
            exc.__class__.__name__,
        )
        return PaymentIntentBookingResult(
            status="lookup_failed",
            message="Could not verify payment confirmation right now",
        )

    status = _payment_intent_value(payment_intent, "status")
    if status != "succeeded":
        if status in {"canceled", "requires_payment_method"}:
            return PaymentIntentBookingResult(
                status="failed",
                message="Payment was not successful",
            )
        return PaymentIntentBookingResult(
            status="processing",
            message="Payment is still being processed",
        )

    try:
        booking, created = create_booking_from_paid_payment_intent(
            db,
            payment_intent,
            cleaned_payment_intent_id,
        )
    except PaymentIntentBookingCreationError as exc:
        logger.error(
            "[PAYMENTS] Paid PaymentIntent could not create Booking: "
            "payment_intent_id=%s error=%s",
            cleaned_payment_intent_id,
            exc,
        )
        return PaymentIntentBookingResult(
            status="recovery_failed",
            message="Payment succeeded, but booking could not be confirmed automatically. Please contact support.",
        )

    return PaymentIntentBookingResult(
        status="confirmed",
        message="Booking confirmed",
        booking=booking,
        created=created,
    )


def retrieve_payment_intent(payment_intent_id: str) -> Any:
    stripe.api_key = require_stripe_secret_key()
    return stripe.PaymentIntent.retrieve(payment_intent_id)


def create_booking_from_paid_payment_intent(
    db: Session,
    payment_intent: Any,
    payment_intent_id: str,
) -> tuple[Booking, bool]:
    metadata = _payment_intent_value(payment_intent, "metadata") or {}
    missing = _missing_metadata_keys(metadata)
    if missing:
        raise PaymentIntentBookingCreationError(f"missing_metadata:{','.join(missing)}")

    _validate_payment_amount(payment_intent, metadata, payment_intent_id)

    try:
        booking_data = BookingCreate(
            service_id=int(_metadata_value(metadata, "service_id")),
            master_id=int(_metadata_value(metadata, "master_id")),
            date=_metadata_value(metadata, "date"),
            time=_metadata_value(metadata, "time"),
            customer_first_name=_metadata_value(metadata, "customer_first_name"),
            customer_last_name=_metadata_value(metadata, "customer_last_name"),
            customer_phone=_metadata_value(metadata, "customer_phone"),
            customer_email=_metadata_value(metadata, "customer_email"),
        )
        deposit_amount_cents = int(_metadata_value(metadata, "deposit_amount_cents"))
        currency = _metadata_value(metadata, "currency")
    except (TypeError, ValueError) as exc:
        raise PaymentIntentBookingCreationError("invalid_metadata") from exc

    created = False

    def on_created(booking: Booking) -> None:
        nonlocal created
        created = True
        send_booking_confirmation_email(booking)

    try:
        booking = create_confirmed_booking(
            db=db,
            data=booking_data,
            source="online",
            deposit_amount_cents=deposit_amount_cents,
            currency=currency,
            stripe_payment_intent_id=payment_intent_id,
            stripe_checkout_session_id=None,
            on_created=on_created,
        )
    except IntegrityError as exc:
        db.rollback()
        existing_booking = get_booking_by_payment_intent(db, payment_intent_id)
        if existing_booking is not None:
            return existing_booking, False
        raise PaymentIntentBookingCreationError("duplicate_payment_intent") from exc
    except HTTPException as exc:
        db.rollback()
        if exc.status_code in {400, 404, 409}:
            logger.error(
                "[PAYMENTS] Paid PaymentIntent could not create Booking because slot is no longer available "
                "payment_intent_id=%s",
                payment_intent_id,
            )
            raise PaymentIntentBookingCreationError("slot_unavailable") from exc
        raise

    return booking, created


def _validate_payment_amount(
    payment_intent: Any,
    metadata: Any,
    payment_intent_id: str,
) -> None:
    try:
        expected_amount = int(_metadata_value(metadata, "deposit_amount_cents"))
    except (TypeError, ValueError) as exc:
        raise PaymentIntentBookingCreationError("invalid_amount_metadata") from exc

    actual_amount = _payment_intent_value(payment_intent, "amount")
    if actual_amount is not None and int(actual_amount) != expected_amount:
        raise PaymentIntentBookingCreationError("amount_mismatch")

    expected_currency = str(_metadata_value(metadata, "currency") or "").lower()
    actual_currency = str(_payment_intent_value(payment_intent, "currency") or "").lower()
    if actual_currency and expected_currency and actual_currency != expected_currency:
        raise PaymentIntentBookingCreationError("currency_mismatch")


def _missing_metadata_keys(metadata: Any) -> list[str]:
    return [
        key
        for key in REQUIRED_PAYMENT_INTENT_METADATA
        if _metadata_value(metadata, key) in (None, "")
    ]


def _metadata_value(metadata: Any, key: str) -> str | None:
    try:
        value = metadata[key]
    except (KeyError, TypeError):
        return None
    if value is None:
        return None
    return str(value)


def _payment_intent_value(payment_intent: Any, key: str) -> Any:
    if isinstance(payment_intent, dict):
        return payment_intent.get(key)
    return getattr(payment_intent, key, None)
