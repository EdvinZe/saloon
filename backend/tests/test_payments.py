from types import SimpleNamespace

import pytest
import stripe
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.bookings.models import Booking
from app.modules.bookings.schemas import BookingCreate
from app.modules.bookings.service import create_confirmed_booking
from app.modules.payments.confirmation_service import (
    confirm_paid_payment_intent_and_create_booking,
)
from tests.conftest import booking_payload, create_booking


pytestmark = pytest.mark.anyio


async def test_payment_result_returns_existing_booking(
    client: AsyncClient,
    db_session: Session,
    seeded_salon,
):
    booking = create_booking(
        db_session,
        seeded_salon,
        payment_intent_id="pi_test_payment_result",
    )

    response = await client.get(
        "/api/bookings/payment-result",
        params={"payment_intent": "pi_test_payment_result"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "confirmed"
    assert payload["booking"]["id"] == booking.id
    assert payload["booking"]["booking_code"] == booking.booking_code
    assert payload["booking"]["manage_token"] == booking.manage_token


async def test_payment_result_unknown_payment_intent_returns_not_found(
    client: AsyncClient,
    db_session: Session,
    monkeypatch,
):
    def raise_not_found(payment_intent_id: str):
        raise stripe.error.InvalidRequestError("No such PaymentIntent", param="id")

    monkeypatch.setattr(
        "app.modules.payments.confirmation_service.retrieve_payment_intent",
        raise_not_found,
    )

    response = await client.get(
        "/api/bookings/payment-result",
        params={"payment_intent": "pi_test_missing"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "not_found"
    assert payload["booking"] is None


def test_duplicate_payment_intent_does_not_create_second_booking(
    db_session: Session,
    seeded_salon,
):
    payload = booking_payload(seeded_salon)
    payment_intent = SimpleNamespace(
        status="succeeded",
        amount=1000,
        currency="eur",
        metadata={
            **{key: str(value) for key, value in payload.items()},
            "deposit_amount_cents": "1000",
            "currency": "EUR",
        },
    )

    first = confirm_paid_payment_intent_and_create_booking(
        db_session,
        "pi_test_duplicate",
        payment_intent=payment_intent,
    )
    second = confirm_paid_payment_intent_and_create_booking(
        db_session,
        "pi_test_duplicate",
        payment_intent=payment_intent,
    )

    bookings = db_session.scalars(
        select(Booking).where(Booking.stripe_payment_intent_id == "pi_test_duplicate")
    ).all()

    assert first.status == "confirmed"
    assert first.created is True
    assert second.status == "confirmed"
    assert second.created is False
    assert first.booking is not None
    assert second.booking is not None
    assert first.booking.id == second.booking.id
    assert len(bookings) == 1


def test_create_confirmed_booking_is_idempotent_for_existing_payment_intent(
    db_session: Session,
    seeded_salon,
):
    data = BookingCreate(**booking_payload(seeded_salon))

    first = create_confirmed_booking(
        db=db_session,
        data=data,
        source="online",
        stripe_payment_intent_id="pi_test_service_idempotency",
    )
    second = create_confirmed_booking(
        db=db_session,
        data=data,
        source="online",
        stripe_payment_intent_id="pi_test_service_idempotency",
    )

    bookings = db_session.scalars(
        select(Booking).where(
            Booking.stripe_payment_intent_id == "pi_test_service_idempotency"
        )
    ).all()

    assert first.id == second.id
    assert len(bookings) == 1


async def test_stripe_webhook_duplicate_payment_intent_is_idempotent(
    client: AsyncClient,
    db_session: Session,
    seeded_salon,
    monkeypatch,
):
    payload = booking_payload(seeded_salon)
    payment_intent = {
        "id": "pi_test_webhook_duplicate",
        "status": "succeeded",
        "amount": 1000,
        "currency": "eur",
        "metadata": {
            **{key: str(value) for key, value in payload.items()},
            "deposit_amount_cents": "1000",
            "currency": "EUR",
        },
    }
    event = {
        "type": "payment_intent.succeeded",
        "data": {"object": payment_intent},
    }

    monkeypatch.setattr(
        "app.modules.payments.webhook_router.stripe.Webhook.construct_event",
        lambda payload, sig_header, secret: event,
    )

    first_response = await client.post(
        "/api/stripe/webhook",
        content=b"{}",
        headers={"Stripe-Signature": "test_signature"},
    )
    second_response = await client.post(
        "/api/stripe/webhook",
        content=b"{}",
        headers={"Stripe-Signature": "test_signature"},
    )

    bookings = db_session.scalars(
        select(Booking).where(
            Booking.stripe_payment_intent_id == "pi_test_webhook_duplicate"
        )
    ).all()

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.json() == {"received": True}
    assert second_response.json() == {"received": True}
    assert len(bookings) == 1
