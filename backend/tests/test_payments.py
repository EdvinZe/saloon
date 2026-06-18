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


def _paid_payment_intent(
    seeded_salon,
    *,
    payment_intent_id: str,
    amount: int = 1000,
    currency: str = "eur",
    metadata_overrides: dict[str, str] | None = None,
) -> dict[str, object]:
    payload = booking_payload(seeded_salon)
    metadata = {
        **{key: str(value) for key, value in payload.items()},
        "deposit_amount_cents": "1000",
        "currency": "EUR",
        **(metadata_overrides or {}),
    }
    return {
        "id": payment_intent_id,
        "status": "succeeded",
        "amount": amount,
        "currency": currency,
        "metadata": metadata,
    }


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


async def test_payment_result_fallback_creates_booking_when_webhook_did_not_arrive(
    client: AsyncClient,
    db_session: Session,
    seeded_salon,
    monkeypatch,
):
    payment_intent = _paid_payment_intent(
        seeded_salon,
        payment_intent_id="pi_test_fallback_creates_booking",
    )
    monkeypatch.setattr(
        "app.modules.payments.confirmation_service.retrieve_payment_intent",
        lambda payment_intent_id: payment_intent,
    )

    response = await client.get(
        "/api/bookings/payment-result",
        params={"payment_intent": "pi_test_fallback_creates_booking"},
    )

    booking = db_session.scalar(
        select(Booking).where(
            Booking.stripe_payment_intent_id == "pi_test_fallback_creates_booking"
        )
    )
    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"
    assert booking is not None
    assert booking.stripe_payment_intent_id == "pi_test_fallback_creates_booking"


async def test_payment_result_rejects_wrong_amount(
    client: AsyncClient,
    db_session: Session,
    seeded_salon,
    monkeypatch,
):
    payment_intent = _paid_payment_intent(
        seeded_salon,
        payment_intent_id="pi_test_wrong_amount",
        amount=500,
    )
    monkeypatch.setattr(
        "app.modules.payments.confirmation_service.retrieve_payment_intent",
        lambda payment_intent_id: payment_intent,
    )

    response = await client.get(
        "/api/bookings/payment-result",
        params={"payment_intent": "pi_test_wrong_amount"},
    )

    booking = db_session.scalar(
        select(Booking).where(Booking.stripe_payment_intent_id == "pi_test_wrong_amount")
    )
    assert response.status_code == 200
    assert response.json()["status"] == "recovery_failed"
    assert booking is None


async def test_payment_result_rejects_wrong_currency(
    client: AsyncClient,
    db_session: Session,
    seeded_salon,
    monkeypatch,
):
    payment_intent = _paid_payment_intent(
        seeded_salon,
        payment_intent_id="pi_test_wrong_currency",
        currency="usd",
    )
    monkeypatch.setattr(
        "app.modules.payments.confirmation_service.retrieve_payment_intent",
        lambda payment_intent_id: payment_intent,
    )

    response = await client.get(
        "/api/bookings/payment-result",
        params={"payment_intent": "pi_test_wrong_currency"},
    )

    booking = db_session.scalar(
        select(Booking).where(
            Booking.stripe_payment_intent_id == "pi_test_wrong_currency"
        )
    )
    assert response.status_code == 200
    assert response.json()["status"] == "recovery_failed"
    assert booking is None


async def test_payment_result_booking_conflict_after_payment_does_not_create_duplicate(
    client: AsyncClient,
    db_session: Session,
    seeded_salon,
    monkeypatch,
):
    existing_booking = create_booking(
        db_session,
        seeded_salon,
        payment_intent_id="pi_test_existing_conflict",
    )
    payment_intent = _paid_payment_intent(
        seeded_salon,
        payment_intent_id="pi_test_conflicting_paid_intent",
    )
    monkeypatch.setattr(
        "app.modules.payments.confirmation_service.retrieve_payment_intent",
        lambda payment_intent_id: payment_intent,
    )

    response = await client.get(
        "/api/bookings/payment-result",
        params={"payment_intent": "pi_test_conflicting_paid_intent"},
    )

    bookings_at_slot = db_session.scalars(
        select(Booking).where(
            Booking.master_id == existing_booking.master_id,
            Booking.start_at == existing_booking.start_at,
            Booking.status == "confirmed",
        )
    ).all()
    conflicting_booking = db_session.scalar(
        select(Booking).where(
            Booking.stripe_payment_intent_id == "pi_test_conflicting_paid_intent"
        )
    )
    assert response.status_code == 200
    assert response.json()["status"] == "recovery_failed"
    assert conflicting_booking is None
    assert len(bookings_at_slot) == 1


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


async def test_successful_stripe_webhook_creates_booking(
    client: AsyncClient,
    db_session: Session,
    seeded_salon,
    monkeypatch,
):
    payment_intent = _paid_payment_intent(
        seeded_salon,
        payment_intent_id="pi_test_webhook_creates_booking",
    )
    event = {
        "type": "payment_intent.succeeded",
        "data": {"object": payment_intent},
    }
    monkeypatch.setattr(
        "app.modules.payments.webhook_router.stripe.Webhook.construct_event",
        lambda payload, sig_header, secret: event,
    )

    response = await client.post(
        "/api/stripe/webhook",
        content=b"{}",
        headers={"Stripe-Signature": "test_signature"},
    )

    booking = db_session.scalar(
        select(Booking).where(
            Booking.stripe_payment_intent_id == "pi_test_webhook_creates_booking"
        )
    )
    assert response.status_code == 200
    assert response.json() == {"received": True}
    assert booking is not None


async def test_stripe_webhook_duplicate_payment_intent_is_idempotent(
    client: AsyncClient,
    db_session: Session,
    seeded_salon,
    monkeypatch,
):
    payment_intent = _paid_payment_intent(
        seeded_salon,
        payment_intent_id="pi_test_webhook_duplicate",
    )
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
