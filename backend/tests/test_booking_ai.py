from datetime import date

import pytest

from app.ai.client import AIDisabledError
from app.ai.schemas import ExtractedBookingIntent


@pytest.mark.anyio
async def test_booking_intent_empty_message_returns_validation_error(client):
    response = await client.post("/api/ai/booking-intent", json={"message": "   "})

    assert response.status_code == 422


@pytest.mark.anyio
async def test_booking_intent_ai_disabled_returns_clean_error(
    client,
    seeded_salon,
    monkeypatch: pytest.MonkeyPatch,
):
    def disabled_ai(**kwargs):
        raise AIDisabledError("AI is disabled")

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        disabled_ai,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={"message": "I want a haircut tomorrow after 3pm"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "AI is disabled"


@pytest.mark.anyio
async def test_booking_intent_returns_schema_with_mocked_provider(
    client,
    seeded_salon,
    monkeypatch: pytest.MonkeyPatch,
):
    captured: dict[str, object] = {}

    def fake_extract_booking_intent(**kwargs):
        captured.update(kwargs)
        return ExtractedBookingIntent(
            intent="find_booking_slot",
            service_query="haircut",
            date=date.today().isoformat(),
            time_preference="after 15:00",
            master_preference=None,
            missing_fields=[],
            assistant_message="I can help look for haircut times after 3pm.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={"message": "  I want a haircut tomorrow after 3pm  "},
    )

    assert response.status_code == 200
    assert response.json() == {
        "intent": "find_booking_slot",
        "service_query": "haircut",
        "date": date.today().isoformat(),
        "time_preference": "after 15:00",
        "master_preference": None,
        "missing_fields": [],
        "assistant_message": "I can help look for haircut times after 3pm.",
    }
    assert captured["user_message"] == "I want a haircut tomorrow after 3pm"
    assert captured["service_names"] == ["Classic Cut"]
    assert captured["today"] == date.today()
