from datetime import date

import pytest

from app.ai.client import AIDisabledError, AIProviderQuotaError
from app.ai.schemas import BookingConversationMessage, CurrentBookingDraft, ExtractedBookingIntent
from tests.booking_ai_helpers import booking_draft_payload


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
            time_preference_type="after",
            time="15:00",
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
        "master_query": None,
        "date": date.today().isoformat(),
        "start_date": None,
        "end_date": None,
        "date_range_type": None,
        "weekdays": None,
        "time_preference": "after 15:00",
        "time_preference_type": "after",
        "time": "15:00",
        "end_time": None,
        "daypart": None,
        "master_preference": None,
        "booking_draft": booking_draft_payload(
            service_query="haircut",
            service_id=None,
            selected_date=date.today().isoformat(),
            time="15:00",
            time_preference="after 15:00",
            time_preference_type="after",
        ),
        "missing_fields": [],
        "next_action": "ready_to_check_availability",
        "assistant_message": (
            f"I understood that you want haircut on {date.today().isoformat()} "
            "at 15:00. I can help you check matching booking options."
        ),
        "requested_time_available": None,
        "available_options": [],
        "nearest_options": [],
        "services": [],
        "masters": [],
        "actions": [],
    }
    assert captured["user_message"] == "I want a haircut tomorrow after 3pm"
    assert captured["service_names"] == ["Classic Cut"]
    assert captured["master_names"] == ["Alex Barber"]
    assert captured["today"] == date.today()
    assert captured["conversation_messages"] == []


@pytest.mark.anyio
async def test_booking_intent_accepts_recent_conversation_context(
    client,
    seeded_salon,
    monkeypatch: pytest.MonkeyPatch,
):
    captured: dict[str, object] = {}

    def fake_extract_booking_intent(**kwargs):
        captured.update(kwargs)
        return ExtractedBookingIntent(
            intent="find_booking_slot",
            service_query="Haircut",
            date=date.today().isoformat(),
            time_preference="at 15:00",
            master_preference=None,
            missing_fields=[],
            assistant_message="I understood that you want a Haircut at 15:00.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={
            "message": "haircut",
            "messages": [
                {"role": "user", "content": "Do you have free time tomorrow at 15"},
                {"role": "assistant", "content": "What service are you looking for?"},
                {"role": "user", "content": "haircut"},
            ],
        },
    )

    assert response.status_code == 200
    assert response.json()["time_preference"] == "at 15:00"
    assert response.json()["time_preference_type"] == "at"
    assert response.json()["time"] == "15:00"
    assert captured["conversation_messages"] == [
        BookingConversationMessage(
            role="user",
            content="Do you have free time tomorrow at 15",
        ),
        BookingConversationMessage(
            role="assistant",
            content="What service are you looking for?",
        ),
        BookingConversationMessage(role="user", content="haircut"),
    ]


@pytest.mark.anyio
async def test_booking_intent_accepts_optional_current_booking_draft(
    client,
    seeded_salon,
    monkeypatch: pytest.MonkeyPatch,
):
    captured: dict[str, object] = {}

    def fake_extract_booking_intent(**kwargs):
        captured.update(kwargs)
        return ExtractedBookingIntent(
            intent="find_booking_slot",
            service_query="Haircut",
            date=date.today().isoformat(),
            time_preference="at 15.00",
            master_preference=None,
            missing_fields=[],
            assistant_message="I can help find matching booking options.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={
            "message": "haircut",
            "current_booking_draft": {
                "service_query": "Haircut",
                "date": date.today().isoformat(),
                "time": "15:00",
                "master_preference": None,
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["time"] == "15:00"
    assert captured["current_booking_draft"] == CurrentBookingDraft(
        service_query="Haircut",
        date=date.today().isoformat(),
        time="15:00",
        master_preference=None,
    )


@pytest.mark.anyio
async def test_booking_intent_provider_quota_returns_clean_error(
    client,
    seeded_salon,
    monkeypatch: pytest.MonkeyPatch,
):
    def quota_ai(**kwargs):
        raise AIProviderQuotaError("AI provider quota is exhausted")

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        quota_ai,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={"message": "hello"},
    )

    assert response.status_code == 429
    assert response.json()["detail"] == "AI provider quota is temporarily exhausted"
