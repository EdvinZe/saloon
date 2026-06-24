from datetime import date, time, timedelta
from decimal import Decimal

import pytest

from app.ai.client import AIProviderError
from app.ai.schemas import ExtractedBookingIntent
from app.modules.master_shifts.models import MasterShift
from app.modules.masters.models import Master, MasterService
from app.modules.services.models import Service


def seed_polish_salon(db_session):
    haircut = Service(
        name="Haircut",
        description="Classic haircut",
        duration_minutes=30,
        cleanup_time_minutes=0,
        price=Decimal("25.00"),
        is_active=True,
        sort_order=1,
    )
    beard = Service(
        name="Beard Trim",
        description="Beard trim",
        duration_minutes=20,
        cleanup_time_minutes=0,
        price=Decimal("15.00"),
        is_active=True,
        sort_order=2,
    )
    alex = Master(
        first_name="Alex",
        last_name="Kravtsov",
        role="Senior Barber",
        bio="",
        initials="AK",
        is_active=True,
        sort_order=1,
    )
    db_session.add_all([haircut, beard, alex])
    db_session.flush()
    db_session.add_all([
        MasterService(master_id=alex.id, service_id=haircut.id),
        MasterService(master_id=alex.id, service_id=beard.id),
    ])
    start_date = date.today() + timedelta(days=1)
    end_date = start_date + timedelta(days=4)
    for offset in range(5):
        shift_date = start_date + timedelta(days=offset)
        db_session.add(
            MasterShift(
                shift_code=f"polish-{shift_date.isoformat()}",
                master_id=alex.id,
                date=shift_date,
                start_time=time(17, 0),
                end_time=time(19, 0),
                status="working",
            )
        )
    db_session.commit()
    return {
        "haircut": haircut,
        "beard": beard,
        "alex": alex,
        "start_date": start_date,
        "end_date": end_date,
    }


@pytest.mark.anyio
async def test_pending_flexible_search_service_continuation_skips_ai_provider(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    data = seed_polish_salon(db_session)
    calls = {"count": 0}

    def fake_extract_booking_intent(**kwargs):
        calls["count"] += 1
        if calls["count"] > 1:
            raise AssertionError("AI provider should not be called for service continuation")
        return ExtractedBookingIntent(
            intent="flexible_availability_search",
            start_date=data["start_date"].isoformat(),
            end_date=data["end_date"].isoformat(),
            date_range_type="date_range",
            weekdays=["monday", "friday"],
            time_preference_type="after",
            time="17:00",
            missing_fields=[],
            assistant_message="Invented slots.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    first = await client.post(
        "/api/ai/booking-intent",
        json={"message": "hi do you have time at monday and friday from 17:00"},
    )
    assert first.status_code == 200
    assert first.json()["assistant_message"] == "What service are you looking for?"

    second = await client.post(
        "/api/ai/booking-intent",
        json={
            "message": "haircut",
            "current_booking_draft": first.json()["booking_draft"],
        },
    )

    assert second.status_code == 200
    body = second.json()
    assert body["intent"] == "flexible_availability_search"
    assert body["service_query"] == "Haircut"
    assert body["available_options"]
    assert "Haircut costs" not in body["assistant_message"]
    assert calls["count"] == 1


@pytest.mark.anyio
async def test_pending_flexible_search_unknown_service_lists_available_services(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    data = seed_polish_salon(db_session)

    def fail_ai(**kwargs):
        raise AssertionError("AI provider should not be called for pending service answer")

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fail_ai,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={
            "message": "dragon cut",
            "current_booking_draft": {
                "date_range_type": "date_range",
                "start_date": data["start_date"].isoformat(),
                "end_date": data["end_date"].isoformat(),
                "time_preference_type": "after",
                "time": "17:00",
            },
        },
    )

    assert response.status_code == 200
    assert "I couldn't find that service" in response.json()["assistant_message"]
    assert "Available services are: Haircut, Beard Trim" in response.json()["assistant_message"]


@pytest.mark.anyio
async def test_ai_provider_unavailable_returns_fallback_and_clean_draft(
    client,
    seeded_salon,
    monkeypatch: pytest.MonkeyPatch,
):
    def unavailable_ai(**kwargs):
        raise AIProviderError("provider down")

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        unavailable_ai,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={
            "message": "haircut",
            "current_booking_draft": {
                "time": "17:00",
                "time_preference": "at 17:00",
                "time_preference_type": "at",
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["booking_draft"]["time"] is None
    assert body["assistant_message"].startswith("AI assistant is temporarily unavailable")
    assert body["actions"] == [
        {"type": "open_booking_form", "label": "Book manually", "payload": {}}
    ]


@pytest.mark.anyio
async def test_greeting_without_active_flow_returns_intro_without_ai(
    client,
    seeded_salon,
    monkeypatch: pytest.MonkeyPatch,
):
    def fail_ai(**kwargs):
        raise AssertionError("AI provider should not be called for simple greeting")

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fail_ai,
    )

    response = await client.post("/api/ai/booking-intent", json={"message": "hi"})

    assert response.status_code == 200
    assert response.json()["assistant_message"] == (
        "Hi! I can help you check services, masters, or available booking times."
    )


@pytest.mark.anyio
async def test_greeting_after_dirty_draft_does_not_return_stale_partial_message(
    client,
    seeded_salon,
    monkeypatch: pytest.MonkeyPatch,
):
    def fail_ai(**kwargs):
        raise AssertionError("AI provider should not be called for simple greeting")

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fail_ai,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={
            "message": "hi",
            "current_booking_draft": {
                "time": "17:00",
                "time_preference": "at 17:00",
                "time_preference_type": "at",
            },
        },
    )

    assert response.status_code == 200
    assert "I have at 17:00 so far" not in response.json()["assistant_message"]
    assert response.json()["booking_draft"]["time"] is None


@pytest.mark.anyio
async def test_service_info_still_works_without_pending_search(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    seed_polish_salon(db_session)

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="service_info",
            service_query="haircut",
            missing_fields=[],
            assistant_message="Haircut info.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    response = await client.post("/api/ai/booking-intent", json={"message": "how much is haircut"})

    assert response.status_code == 200
    assert response.json()["intent"] == "service_info"
    assert "Haircut costs €25" in response.json()["assistant_message"]


@pytest.mark.anyio
async def test_flexible_search_still_works(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    seed_polish_salon(db_session)

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
        json={"message": "I need a haircut Monday to Friday after 5pm"},
    )

    assert response.status_code == 200
    assert response.json()["available_options"]
