import logging
from datetime import date

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
    metadata = dict(payment_intent["metadata"] or {})

    logger.info(
        "[STRIPE] payment_intent.succeeded received: payment_intent_id=%s",
        payment_intent_id,
    )
    logger.info("[STRIPE] PaymentIntent metadata keys: %s", list(metadata.keys()))

    missing_metadata = REQUIRED_PAYMENT_INTENT_METADATA - set(metadata.keys())
    if missing_metadata:
        logger.error(
            "[STRIPE] Missing required metadata for booking creation: missing=%s "
            "payment_intent_id=%s",
            sorted(missing_metadata),
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
            service_id=int(metadata["service_id"]),
            master_id=int(metadata["master_id"]),
            date=date.fromisoformat(metadata["date"]),
            time=metadata["time"],
            customer_first_name=metadata["customer_first_name"],
            customer_last_name=metadata["customer_last_name"],
            customer_phone=metadata["customer_phone"],
            customer_email=metadata["customer_email"],
        )
        deposit_amount_cents = int(metadata["deposit_amount_cents"])
        currency = metadata["currency"]
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
