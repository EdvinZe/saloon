import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.core import config
from app.core.rate_limit import (
    ADMIN_LOGIN_RATE_LIMIT,
    MANAGE_RATE_LIMIT,
    PAYMENT_RATE_LIMIT,
    PUBLIC_RATE_LIMIT,
)
from app.modules.admin_auth.passwords import hash_admin_password
from tests.conftest import booking_payload, create_booking


pytestmark = pytest.mark.anyio


async def test_public_endpoint_allows_requests_below_limit(
    client: AsyncClient,
):
    responses = [
        await client.get("/api/services/public")
        for _ in range(PUBLIC_RATE_LIMIT.limit)
    ]

    assert all(response.status_code == 200 for response in responses)


async def test_public_endpoint_returns_429_after_limit(
    client: AsyncClient,
):
    for _ in range(PUBLIC_RATE_LIMIT.limit):
        response = await client.get("/api/services/public")
        assert response.status_code == 200

    limited_response = await client.get("/api/services/public")

    assert limited_response.status_code == 429
    assert (
        limited_response.json()["detail"]
        == "Rate limit exceeded. Please try again later."
    )


async def test_payment_endpoint_returns_429_after_payment_limit(
    client: AsyncClient,
    seeded_salon,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(
        "app.modules.bookings.router.create_booking_deposit_payment_intent",
        lambda data: {
            "client_secret": "pi_test_secret",
            "payment_intent_id": "pi_test_rate_limit",
        },
    )

    for _ in range(PAYMENT_RATE_LIMIT.limit):
        response = await client.post(
            "/api/bookings/deposit-intent",
            json=booking_payload(seeded_salon),
        )
        assert response.status_code == 200

    limited_response = await client.post(
        "/api/bookings/deposit-intent",
        json=booking_payload(seeded_salon),
    )

    assert limited_response.status_code == 429


async def test_manage_endpoint_returns_429_after_manage_limit(
    client: AsyncClient,
    db_session: Session,
    seeded_salon,
):
    booking = create_booking(db_session, seeded_salon)

    for _ in range(MANAGE_RATE_LIMIT.limit):
        response = await client.get(
            "/api/bookings/manage",
            params={"token": booking.manage_token},
        )
        assert response.status_code == 200

    limited_response = await client.get(
        "/api/bookings/manage",
        params={"token": booking.manage_token},
    )

    assert limited_response.status_code == 429


async def test_admin_login_returns_429_after_too_many_failed_attempts(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr("app.modules.admin_auth.service.ADMIN_USERNAME", "admin")
    monkeypatch.setattr(
        "app.modules.admin_auth.service.ADMIN_PASSWORD_HASH",
        hash_admin_password("correct-password"),
    )
    monkeypatch.setattr("app.modules.admin_auth.service.ADMIN_PASSWORD", "")

    for _ in range(ADMIN_LOGIN_RATE_LIMIT.limit):
        response = await client.post(
            "/api/admin/auth/login",
            json={"username": "admin", "password": "wrong-password"},
        )
        assert response.status_code == 401

    limited_response = await client.post(
        "/api/admin/auth/login",
        json={"username": "admin", "password": "wrong-password"},
    )

    assert limited_response.status_code == 429
    assert "Too many failed login attempts" in limited_response.json()["detail"]


async def test_rate_limiting_can_be_disabled(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(config, "RATE_LIMIT_ENABLED", False)

    responses = [
        await client.get("/api/services/public")
        for _ in range(PUBLIC_RATE_LIMIT.limit + 1)
    ]

    assert all(response.status_code == 200 for response in responses)
