from datetime import date, time, timedelta
from decimal import Decimal

import pytest

from app.ai.schemas import ExtractedBookingIntent
from app.modules.master_shifts.models import MasterShift
from app.modules.masters.models import Master, MasterService
from app.modules.services.models import Service


def seed_weekday_salon(db_session):
    service = Service(
        name="Haircut",
        description="Classic haircut",
        duration_minutes=30,
        cleanup_time_minutes=0,
        price=Decimal("25.00"),
        is_active=True,
        sort_order=1,
    )
    master = Master(
        first_name="Alex",
        last_name="Kravtsov",
        role="Senior Barber",
        bio="",
        initials="AK",
        is_active=True,
        sort_order=1,
    )
    db_session.add_all([service, master])
    db_session.flush()
    db_session.add(MasterService(master_id=master.id, service_id=service.id))

    today = date.today()
    monday = today - timedelta(days=today.weekday())
    days = {
        "monday": monday,
        "tuesday": monday + timedelta(days=1),
        "wednesday": monday + timedelta(days=2),
        "thursday": monday + timedelta(days=3),
        "friday": monday + timedelta(days=4),
        "saturday": monday + timedelta(days=5),
    }
    for name, shift_date in days.items():
        db_session.add(
            MasterShift(
                shift_code=f"weekday-{name}-{shift_date.isoformat()}",
                master_id=master.id,
                date=shift_date,
                start_time=time(17, 0),
                end_time=time(18, 0),
                status="working",
            )
        )
    db_session.commit()
    return {"service": service, "master": master, **days}


@pytest.mark.anyio
async def test_tuesday_to_friday_wording_and_expansion(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    data = seed_weekday_salon(db_session)

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="flexible_availability_search",
            service_query="haircut",
            date_range_type="weekdays",
            weekdays=["monday", "tuesday", "wednesday", "thursday", "friday"],
            time_preference_type="at",
            time="17:00",
            missing_fields=[],
            assistant_message="Slots.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={"message": "what time do you have from tuesday to friday from 17:00"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "from Tuesday to Friday" in body["assistant_message"]
    assert "from 17:00" in body["assistant_message"]
    assert "weekdays" not in body["assistant_message"]
    option_dates = {option["date"] for option in body["available_options"]}
    assert option_dates <= {
        data["tuesday"].isoformat(),
        data["wednesday"].isoformat(),
        data["thursday"].isoformat(),
        data["friday"].isoformat(),
    }
    assert data["monday"].isoformat() not in option_dates
    assert data["saturday"].isoformat() not in option_dates


@pytest.mark.anyio
async def test_monday_and_friday_wording_and_expansion(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    data = seed_weekday_salon(db_session)

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="flexible_availability_search",
            service_query="haircut",
            date_range_type="weekdays",
            weekdays=["monday", "tuesday", "wednesday", "thursday", "friday"],
            time_preference_type="after",
            time="17:00",
            missing_fields=[],
            assistant_message="Slots.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={"message": "do you have time at monday and friday from 17:00"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "on Monday and Friday" in body["assistant_message"]
    assert "from 17:00" in body["assistant_message"]
    assert "weekdays" not in body["assistant_message"]
    option_dates = {option["date"] for option in body["available_options"]}
    assert option_dates <= {data["monday"].isoformat(), data["friday"].isoformat()}
    assert data["thursday"].isoformat() not in option_dates


@pytest.mark.anyio
async def test_weekday_typo_mondau_is_normalized(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    seed_weekday_salon(db_session)

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="flexible_availability_search",
            service_query="haircut",
            date_range_type="weekdays",
            time_preference_type="after",
            time="17:00",
            missing_fields=[],
            assistant_message="Slots.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={"message": "do you have time at mondau and friday from 17:00"},
    )

    assert response.status_code == 200
    assert "on Monday and Friday" in response.json()["assistant_message"]


@pytest.mark.anyio
async def test_exact_time_wording_uses_at(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    seed_weekday_salon(db_session)

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="flexible_availability_search",
            service_query="haircut",
            date_range_type="selected_weekdays",
            weekdays=["friday"],
            time_preference_type="at",
            time="17:00",
            missing_fields=[],
            assistant_message="Slots.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={"message": "do you have haircut at 17:00 on friday"},
    )

    assert response.status_code == 200
    assert "at 17:00" in response.json()["assistant_message"]


@pytest.mark.anyio
async def test_new_explicit_search_resets_pagination_wording(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    data = seed_weekday_salon(db_session)

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="flexible_availability_search",
            service_query="haircut",
            date_range_type="weekdays",
            time_preference_type="after",
            time="17:00",
            missing_fields=[],
            assistant_message="Slots.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={
            "message": "do you have time at monday and friday from 17:00",
            "current_booking_draft": {
                "service_query": "Haircut",
                "service_id": data["service"].id,
                "date_range_type": "nearest",
                "shown_option_count": 3,
                "last_intent": "flexible_availability_search",
            },
        },
    )

    assert response.status_code == 200
    assert "Here are more" not in response.json()["assistant_message"]
    assert response.json()["assistant_message"].startswith("I found") or response.json()["assistant_message"].startswith("I couldn't find")
    assert response.json()["booking_draft"]["shown_option_count"] <= 3


@pytest.mark.anyio
async def test_pending_search_uses_specific_weekday_range_after_service_answer(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    seed_weekday_salon(db_session)

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="flexible_availability_search",
            date_range_type="weekdays",
            weekdays=["monday", "tuesday", "wednesday", "thursday", "friday"],
            time_preference_type="after",
            time="17:00",
            missing_fields=[],
            assistant_message="Slots.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    first = await client.post(
        "/api/ai/booking-intent",
        json={"message": "do you have time from tuesday to friday from 17:00"},
    )
    second = await client.post(
        "/api/ai/booking-intent",
        json={
            "message": "haircut",
            "current_booking_draft": first.json()["booking_draft"],
        },
    )

    assert second.status_code == 200
    assert "from Tuesday to Friday" in second.json()["assistant_message"]
