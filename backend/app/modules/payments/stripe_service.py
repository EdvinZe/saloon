import logging

import stripe

from app.core.config import require_stripe_secret_key
from app.modules.bookings.schemas import BookingCreate

logger = logging.getLogger(__name__)

DEPOSIT_AMOUNT_CENTS = 1000
CURRENCY = "EUR"


def create_booking_deposit_payment_intent(data: BookingCreate) -> dict[str, str]:
    stripe.api_key = require_stripe_secret_key()

    payment_intent = stripe.PaymentIntent.create(
        amount=DEPOSIT_AMOUNT_CENTS,
        currency=CURRENCY.lower(),
        automatic_payment_methods={"enabled": True},
        receipt_email=data.customer_email,
        metadata={
            "service_id": str(data.service_id),
            "master_id": str(data.master_id),
            "date": data.date.isoformat(),
            "time": data.time,
            "customer_first_name": data.customer_first_name,
            "customer_last_name": data.customer_last_name,
            "customer_phone": data.customer_phone,
            "customer_email": data.customer_email,
            "deposit_amount_cents": str(DEPOSIT_AMOUNT_CENTS),
            "currency": CURRENCY,
        },
    )

    logger.info(
        "[STRIPE] Deposit PaymentIntent created: payment_intent_id=%s "
        "service_id=%s master_id=%s",
        payment_intent.id,
        data.service_id,
        data.master_id,
    )

    return {
        "client_secret": payment_intent.client_secret,
        "payment_intent_id": payment_intent.id,
    }
