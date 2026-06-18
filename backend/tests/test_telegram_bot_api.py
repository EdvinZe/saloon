from datetime import date, time

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.modules.master_shifts.models import MasterShift
from app.modules.masters.models import Master, MasterService
from app.modules.services.models import Service
from app.modules.telegram_accounts.models import TelegramAccount
from tests.conftest import create_booking


pytestmark = pytest.mark.anyio

BOT_TOKEN = "test-bot-secret"
BOT_HEADERS = {"X-Telegram-Bot-Token": BOT_TOKEN}


async def test_bot_endpoint_without_secret_is_rejected(client: AsyncClient):
    response = await client.get(
        "/api/bot/telegram-accounts/resolve",
        params={"telegram_id": 1001},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Telegram bot token is required"


async def test_bot_endpoint_with_wrong_secret_is_rejected(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", BOT_TOKEN)

    response = await client.get(
        "/api/bot/telegram-accounts/resolve",
        params={"telegram_id": 1001},
        headers={"X-Telegram-Bot-Token": "wrong-secret"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Telegram bot token is invalid"


async def test_bot_endpoint_with_correct_secret_can_resolve_allowed_account(
    client: AsyncClient,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", BOT_TOKEN)
    _add_telegram_account(db_session, telegram_id=1001, role="manager")

    response = await client.get(
        "/api/bot/telegram-accounts/resolve",
        params={"telegram_id": 1001},
        headers=BOT_HEADERS,
    )

    assert response.status_code == 200
    assert response.json()["authorized"] is True
    assert response.json()["role"] == "manager"
    assert response.json()["scope"] == "all"


async def test_inactive_telegram_account_is_denied(
    client: AsyncClient,
    db_session: Session,
    seeded_salon,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", BOT_TOKEN)
    _add_telegram_account(
        db_session,
        telegram_id=1002,
        role="barber",
        master_id=seeded_salon["master"].id,
        is_active=False,
    )

    response = await client.get(
        "/api/bot/telegram-accounts/bookings",
        params={"telegram_id": 1002},
        headers=BOT_HEADERS,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Telegram account is not authorized"


async def test_barber_account_sees_only_own_bookings(
    client: AsyncClient,
    db_session: Session,
    seeded_salon,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", BOT_TOKEN)
    own_booking, other_booking = _create_two_master_bookings(db_session, seeded_salon)
    _add_telegram_account(
        db_session,
        telegram_id=1003,
        role="barber",
        master_id=own_booking.master_id,
    )

    response = await client.get(
        "/api/bot/telegram-accounts/bookings",
        params={
            "telegram_id": 1003,
            "date": own_booking.start_at.date().isoformat(),
            "status": "confirmed",
        },
        headers=BOT_HEADERS,
    )

    booking_ids = {booking["id"] for booking in response.json()}
    assert response.status_code == 200
    assert own_booking.id in booking_ids
    assert other_booking.id not in booking_ids


async def test_manager_account_sees_all_bookings(
    client: AsyncClient,
    db_session: Session,
    seeded_salon,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", BOT_TOKEN)
    own_booking, other_booking = _create_two_master_bookings(db_session, seeded_salon)
    _add_telegram_account(db_session, telegram_id=1004, role="manager")

    response = await client.get(
        "/api/bot/telegram-accounts/bookings",
        params={
            "telegram_id": 1004,
            "date": own_booking.start_at.date().isoformat(),
            "status": "confirmed",
        },
        headers=BOT_HEADERS,
    )

    booking_ids = {booking["id"] for booking in response.json()}
    assert response.status_code == 200
    assert own_booking.id in booking_ids
    assert other_booking.id in booking_ids


def _add_telegram_account(
    db_session: Session,
    *,
    telegram_id: int,
    role: str,
    master_id: int | None = None,
    is_active: bool = True,
) -> TelegramAccount:
    account = TelegramAccount(
        telegram_id=telegram_id,
        role=role,
        first_name="Test",
        last_name="User",
        master_id=master_id,
        is_active=is_active,
    )
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)
    return account


def _create_two_master_bookings(db_session: Session, seeded_salon):
    own_booking = create_booking(
        db_session,
        seeded_salon,
        payment_intent_id="pi_test_bot_own_booking",
    )

    service = seeded_salon["service"]
    selected_date = seeded_salon["date"]
    assert isinstance(service, Service)
    assert isinstance(selected_date, date)

    other_master = Master(
        first_name="Morgan",
        last_name="Clipper",
        role="Barber",
        bio="",
        initials="MC",
        is_active=True,
        sort_order=2,
    )
    db_session.add(other_master)
    db_session.flush()
    db_session.add(MasterService(master_id=other_master.id, service_id=service.id))
    db_session.add(
        MasterShift(
            shift_code=f"shift-{other_master.id}-{selected_date.isoformat()}",
            master_id=other_master.id,
            date=selected_date,
            start_time=time(10, 0),
            end_time=time(12, 0),
            status="working",
        )
    )
    db_session.commit()

    other_booking = create_booking(
        db_session,
        {
            **seeded_salon,
            "master": other_master,
        },
        payment_intent_id="pi_test_bot_other_booking",
    )
    return own_booking, other_booking
