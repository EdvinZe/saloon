import pytest

from app.ai.schemas import ExtractedBookingIntent
from app.modules.bookings.models import Booking
from tests.booking_ai_helpers import booking_draft_payload


@pytest.mark.anyio
async def test_booking_intent_available_master_question_does_not_claim_live_check(
    client,
    seeded_salon,
    monkeypatch: pytest.MonkeyPatch,
):
    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="check_available_masters",
            service_query="haircut",
            date=None,
            time_preference=None,
            master_preference=None,
            missing_fields=[],
            assistant_message="I'm checking which master is available...",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )
    selected_date = seeded_salon["date"].isoformat()

    response = await client.post(
        "/api/ai/booking-intent",
        json={
            "message": "what master can do at this time haircut",
            "current_booking_draft": booking_draft_payload(
                service_query="haircut",
                service_id=None,
                selected_date=selected_date,
                time="15:00",
                time_preference="at 15:00",
                time_preference_type="at",
            ),
        },
    )

    assert response.status_code == 200
    assert response.json()["booking_draft"]["service_query"] == "Classic Cut"
    assert response.json()["booking_draft"]["service_id"] == seeded_salon["service"].id
    assert response.json()["booking_draft"]["date"] == selected_date
    assert response.json()["booking_draft"]["time"] == "15:00"
    assert response.json()["next_action"] in {"availability_alternatives", "ready_to_check_availability"}
    assistant_message = response.json()["assistant_message"]
    assert "I'm checking" not in assistant_message
    assert "I found" not in assistant_message


@pytest.mark.anyio
async def test_booking_intent_check_exact_time_available_uses_read_only_availability(
    client,
    db_session,
    seeded_salon,
    monkeypatch: pytest.MonkeyPatch,
):
    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="check_available_masters",
            service_query=None,
            date=None,
            time_preference=None,
            master_preference=None,
            missing_fields=[],
            assistant_message="Checking...",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )
    service = seeded_salon["service"]
    master = seeded_salon["master"]
    selected_date = seeded_salon["date"]
    before_count = db_session.query(Booking).count()

    response = await client.post(
        "/api/ai/booking-intent",
        json={
            "message": "check",
            "current_booking_draft": booking_draft_payload(
                service_query="haircut",
                selected_date=selected_date.isoformat(),
                time="10:00",
                time_preference="at 10:00",
                time_preference_type="at",
            ),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["next_action"] == "availability_found"
    assert body["requested_time_available"] is True
    assert body["booking_draft"]["service_id"] == service.id
    assert body["booking_draft"]["master_id"] == master.id
    assert body["booking_draft"]["master_name"] == "Alex Barber"
    assert body["available_options"] == [
        {
            "service_id": service.id,
            "service_name": service.name,
            "master_id": master.id,
            "master_name": "Alex Barber",
            "date": selected_date.isoformat(),
            "time": "10:00",
        }
    ]
    assert "Good news" in body["assistant_message"]
    assert "available" in body["assistant_message"]
    assert "confirm it" in body["assistant_message"]
    assert db_session.query(Booking).count() == before_count


@pytest.mark.anyio
async def test_booking_intent_check_exact_time_unavailable_returns_nearest_options(
    client,
    db_session,
    seeded_salon,
    monkeypatch: pytest.MonkeyPatch,
):
    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="check_available_masters",
            service_query=None,
            date=None,
            time_preference=None,
            master_preference=None,
            missing_fields=[],
            assistant_message="Checking...",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )
    selected_date = seeded_salon["date"]
    before_count = db_session.query(Booking).count()

    response = await client.post(
        "/api/ai/booking-intent",
        json={
            "message": "is this time available?",
            "current_booking_draft": booking_draft_payload(
                service_query="haircut",
                selected_date=selected_date.isoformat(),
                time="12:00",
                time_preference="at 12:00",
                time_preference_type="at",
            ),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["next_action"] == "availability_alternatives"
    assert body["requested_time_available"] is False
    assert body["available_options"] == []
    assert body["nearest_options"]
    assert body["nearest_options"][0]["direction"] == "before"
    assert body["nearest_options"][0]["time"] == "11:30"
    assert body["nearest_options"][0]["service_id"] == seeded_salon["service"].id
    assert body["nearest_options"][0]["service_name"] == seeded_salon["service"].name
    assert "12:00 is not available" in body["assistant_message"]
    assert "closest available options" in body["assistant_message"]
    assert db_session.query(Booking).count() == before_count
