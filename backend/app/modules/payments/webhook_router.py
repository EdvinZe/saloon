import logging

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import require_stripe_webhook_secret
from app.core.database import get_db
from app.modules.payments.confirmation_service import (
    confirm_paid_payment_intent_and_create_booking,
)

logger = logging.getLogger(__name__)

router = APIRouter()

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

    logger.info(
        "[STRIPE] payment_intent.succeeded received: payment_intent_id=%s",
        payment_intent_id,
    )

    result = confirm_paid_payment_intent_and_create_booking(
        db,
        payment_intent_id,
        payment_intent=payment_intent,
    )
    if result.booking is not None and not result.created:
        logger.info(
            "[STRIPE] Booking already exists for payment_intent_id=%s",
            payment_intent_id,
        )
        return

    if result.booking is None:
        logger.error(
            "[STRIPE] Paid deposit received but booking could not be created: "
            "payment_intent_id=%s status=%s message=%s",
            payment_intent_id,
            result.status,
            result.message,
        )
        return

    logger.info(
        "[STRIPE] Booking created from deposit payment: booking_code=%s "
        "payment_intent_id=%s",
        result.booking.booking_code,
        payment_intent_id,
    )
