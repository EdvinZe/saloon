from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.core import config
from app.modules.admin_auth.passwords import hash_admin_password
from tests.conftest import create_booking


pytestmark = pytest.mark.anyio


async def test_admin_hashed_password_login_succeeds_and_wrong_password_fails(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr("app.modules.admin_auth.service.ADMIN_USERNAME", "admin")
    monkeypatch.setattr(
        "app.modules.admin_auth.service.ADMIN_PASSWORD_HASH",
        hash_admin_password("correct-password"),
    )
    monkeypatch.setattr("app.modules.admin_auth.service.ADMIN_PASSWORD", "fallback")

    wrong_response = await client.post(
        "/api/admin/auth/login",
        json={"username": "admin", "password": "fallback"},
    )
    correct_response = await client.post(
        "/api/admin/auth/login",
        json={"username": "admin", "password": "correct-password"},
    )

    assert wrong_response.status_code == 401
    assert correct_response.status_code == 200
    assert correct_response.json()["authenticated"] is True
    assert "admin_session=" in correct_response.headers["set-cookie"]
    assert "HttpOnly" in correct_response.headers["set-cookie"]


async def test_manage_cutoff_uses_configured_backend_value(
    client: AsyncClient,
    db_session: Session,
    seeded_salon,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(
        "app.modules.bookings.service.get_client_manage_cutoff_hours",
        lambda: 12,
    )
    booking = create_booking(db_session, seeded_salon)
    booking.start_at = datetime.now() + timedelta(hours=6)
    booking.end_at = booking.start_at + timedelta(minutes=30)
    db_session.commit()
    db_session.refresh(booking)

    response = await client.post(
        "/api/bookings/manage/cancel",
        json={"token": booking.manage_token},
    )

    assert response.status_code == 400
    assert "12 hours before the appointment" in response.json()["detail"]


async def test_manage_responses_do_not_expose_manage_token(
    client: AsyncClient,
    db_session: Session,
    seeded_salon,
):
    view_booking = create_booking(
        db_session,
        seeded_salon,
        payment_intent_id="pi_test_manage_view",
    )

    view_response = await client.get(
        "/api/bookings/manage",
        params={"token": view_booking.manage_token},
    )

    assert view_response.status_code == 200
    _assert_no_manage_token(view_response.json(), view_booking.id)
    view_booking.status = "cancelled"
    db_session.commit()

    reschedule_booking = create_booking(
        db_session,
        seeded_salon,
        payment_intent_id="pi_test_manage_reschedule",
    )
    reschedule_response = await client.post(
        "/api/bookings/manage/reschedule",
        json={
            "token": reschedule_booking.manage_token,
            "master_id": reschedule_booking.master_id,
            "date": reschedule_booking.start_at.date().isoformat(),
            "time": reschedule_booking.start_at.strftime("%H:%M"),
        },
    )

    assert reschedule_response.status_code == 200
    _assert_no_manage_token(
        reschedule_response.json()["booking"],
        reschedule_booking.id,
    )
    reschedule_booking.status = "cancelled"
    db_session.commit()

    cancel_booking = create_booking(
        db_session,
        seeded_salon,
        payment_intent_id="pi_test_manage_cancel",
    )
    cancel_booking.deposit_status = "retained"
    cancel_booking.stripe_payment_intent_id = None
    db_session.commit()
    db_session.refresh(cancel_booking)
    cancel_response = await client.post(
        "/api/bookings/manage/cancel",
        json={"token": cancel_booking.manage_token},
    )

    assert cancel_response.status_code == 200
    _assert_no_manage_token(cancel_response.json()["booking"], cancel_booking.id)


async def test_security_headers_are_applied(client: AsyncClient):
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"
    assert (
        response.headers["permissions-policy"]
        == "camera=(), microphone=(), geolocation=()"
    )


async def test_large_request_body_returns_413(client: AsyncClient):
    response = await client.post(
        "/api/bookings/check-availability",
        content=b"x" * (config.MAX_REQUEST_BODY_BYTES + 1),
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 413
    assert response.json()["detail"] == "Request body too large"


def test_production_cors_does_not_allow_wildcard(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(config, "APP_ENV", "production")
    monkeypatch.setattr(config, "CORS_ALLOWED_ORIGINS", ["*"])

    assert config.get_cors_allowed_origins() == []


def _assert_no_manage_token(payload: dict[str, object], booking_id: int) -> None:
    assert payload["id"] == booking_id
    assert "manage_token" not in payload
    assert "manage_url" not in payload
