import logging

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import require_stripe_webhook_secret
from app.core.database import get_db
from app.modules.bookings.models import Booking
from app.modules.bookings.schemas import BookingCreate
from app.modules.bookings.service import create_confirmed_booking

logger = logging.getLogger(__name__)

router = APIRouter()

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


def _metadata_value(metadata, key: str) -> str | None:
    try:
        value = metadata[key]
    except KeyError:
        return None

    if value is None:
        return None

    return str(value)


def _missing_metadata_keys(metadata) -> list[str]:
    return [
        key
        for key in REQUIRED_PAYMENT_INTENT_METADATA
        if _metadata_value(metadata, key) in (None, "")
    ]


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str | None = Header(default=None, alias="Stripe-Signature"),
    db: Session = Depends(get_db),
):
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload,
            stripe_signature,
            require_stripe_webhook_secret(),
        )
    except (ValueError, stripe.error.SignatureVerificationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Stripe webhook signature",
        ) from exc

    event_type = event["type"]
    logger.info("[STRIPE] Webhook received: event_type=%s", event_type)

    if event_type == "payment_intent.succeeded":
        _handle_payment_intent_succeeded(db, event["data"]["object"])

    return {"received": True}


def _handle_payment_intent_succeeded(db: Session, payment_intent) -> None:
    payment_intent_id = payment_intent["id"]
    metadata = payment_intent["metadata"] or {}

    logger.info(
        "[STRIPE] payment_intent.succeeded received: payment_intent_id=%s",
        payment_intent_id,
    )

    missing = _missing_metadata_keys(metadata)
    if missing:
        logger.error(
            "[STRIPE] Missing required metadata for booking creation: missing=%s payment_intent_id=%s",
            missing,
            payment_intent_id,
        )
        return

    existing_booking = db.scalar(
        select(Booking).where(Booking.stripe_payment_intent_id == payment_intent_id)
    )
    if existing_booking is not None:
        logger.info(
            "[STRIPE] Booking already exists for payment_intent_id=%s",
            payment_intent_id,
        )
        return

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
        logger.error(
            "[STRIPE] Invalid metadata for booking creation: "
            "payment_intent_id=%s error=%s",
            payment_intent_id,
            exc,
        )
        return

    try:
        booking = create_confirmed_booking(
            db=db,
            data=booking_data,
            source="online",
            deposit_amount_cents=deposit_amount_cents,
            currency=currency,
            stripe_payment_intent_id=payment_intent_id,
            stripe_checkout_session_id=None,
        )
    except HTTPException as exc:
        logger.error(
            "[STRIPE] Paid deposit received but booking could not be created: "
            "payment_intent_id=%s status_code=%s detail=%s",
            payment_intent_id,
            exc.status_code,
            exc.detail,
        )
        # TODO: add automatic refund/manual handling for paid deposit when booking creation fails.
        db.rollback()
        return
    except Exception:
        logger.exception(
            "[STRIPE] Unexpected webhook error while creating booking: "
            "payment_intent_id=%s",
            payment_intent_id,
        )
        db.rollback()
        raise

    logger.info(
        "[STRIPE] Booking created from deposit payment: booking_code=%s "
        "payment_intent_id=%s",
        booking.booking_code,
        payment_intent_id,
    )
