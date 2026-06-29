from datetime import date
import importlib
import logging

import pytest

from app.ai.client import AIDisabledError, AIProviderQuotaError
from app.ai.schemas import BookingConversationMessage, CurrentBookingDraft, ExtractedBookingIntent
from tests.booking_ai_helpers import booking_draft_payload


def reload_ai_debug_config(monkeypatch: pytest.MonkeyPatch, value: str | None):
    if value is None:
        monkeypatch.delenv("AI_DEBUG", raising=False)
    else:
        monkeypatch.setenv("AI_DEBUG", value)

    import app.core.config as config

    return importlib.reload(config)


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

    assert response.status_code == 200
    assert response.json()["assistant_message"] == (
        "AI assistant is temporarily unavailable right now, but the booking system is still working normally. "
        "You can continue by using the booking form."
    )
    assert response.json()["booking_draft"] == booking_draft_payload()
    assert response.json()["actions"] == [
        {"type": "open_booking_form", "label": "Book manually", "payload": {}}
    ]


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
async def test_booking_intent_debug_logs_request_and_parsed_intent(
    client,
    seeded_salon,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
):
    reload_ai_debug_config(monkeypatch, None)

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="find_booking_slot",
            service_query="Haircut",
            date=date.today().isoformat(),
            time_preference="at 18:00",
            time_preference_type="at",
            time="18:00",
            missing_fields=[],
            assistant_message="I can help find that time.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )
    caplog.set_level(logging.INFO, logger="app.ai.booking_debug")

    response = await client.post(
        "/api/ai/booking-intent",
        json={
            "message": "i want at 18:00",
            "messages": [
                {"role": "user", "content": "I want a Haircut"},
                {"role": "assistant", "content": "What date works?"},
            ],
            "current_booking_draft": {
                "service_query": "Haircut",
                "service_id": 1,
                "date": date.today().isoformat(),
                "time": None,
                "time_preference": None,
                "last_intent": "flexible_availability_search",
            },
        },
    )

    assert response.status_code == 200
    assert "USER MESSAGE" in caplog.text
    assert 'text: "i want at 18:00"' in caplog.text
    assert "conversation_messages_count: 2" in caplog.text
    assert "incoming_draft:" in caplog.text
    assert "service: Haircut" in caplog.text
    assert f"date: {date.today().isoformat()}" in caplog.text
    assert "<redacted-phone>" not in caplog.text
    assert "PARSED MODEL OUTPUT" in caplog.text
    assert "intent: find_booking_slot" in caplog.text
    assert "time: 18:00" in caplog.text
    assert "FINAL RESPONSE" in caplog.text


@pytest.mark.anyio
async def test_booking_intent_debug_logs_disabled_when_ai_debug_false(
    client,
    seeded_salon,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
):
    reload_ai_debug_config(monkeypatch, "false")

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="find_booking_slot",
            service_query="Haircut",
            date=date.today().isoformat(),
            time_preference="at 18:00",
            time_preference_type="at",
            time="18:00",
            missing_fields=[],
            assistant_message="I can help find that time.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )
    caplog.set_level(logging.INFO, logger="app.ai.booking_debug")

    response = await client.post(
        "/api/ai/booking-intent",
        json={"message": "i want a haircut at 18:00"},
    )

    assert response.status_code == 200
    assert "ai_booking_" not in caplog.text


@pytest.mark.anyio
async def test_booking_intent_debug_logs_local_response_skips_model(
    client,
    seeded_salon,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
):
    reload_ai_debug_config(monkeypatch, None)

    def fail_extract_booking_intent(**kwargs):
        raise AssertionError("AI provider should not be called for simple greeting")

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fail_extract_booking_intent,
    )
    caplog.set_level(logging.INFO, logger="app.ai.booking_debug")

    response = await client.post(
        "/api/ai/booking-intent",
        json={
            "message": "hey",
            "messages": [
                {"role": "user", "content": "hello"},
                {"role": "assistant", "content": "Hi!"},
            ],
        },
    )

    assert response.status_code == 200
    assert "USER MESSAGE" in caplog.text
    assert 'text: "hey"' in caplog.text
    assert "conversation_messages_count: 2" in caplog.text
    assert "BACKEND DECISION" in caplog.text
    assert "handler: build_local_pre_ai_response" in caplog.text
    assert "model_call: skipped" in caplog.text
    assert "FINAL RESPONSE" in caplog.text
    assert "intent: greeting" in caplog.text
    assert "END TRACE" in caplog.text


@pytest.mark.anyio
async def test_booking_intent_unknown_preserves_safe_model_message(
    client,
    seeded_salon,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
):
    model_message = (
        "I didn't understand your request. "
        "Can you please ask about services, masters, or booking times?"
    )

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="unknown",
            missing_fields=[],
            assistant_message=model_message,
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )
    caplog.set_level(logging.INFO, logger="app.ai.booking_debug")

    response = await client.post(
        "/api/ai/booking-intent",
        json={"message": "i want tolik"},
    )

    assert response.status_code == 200
    assert response.json()["assistant_message"] == model_message
    assert response.json()["next_action"] == "none"
    assert "used safe model assistant_message for generic conversational response" in caplog.text


@pytest.mark.anyio
async def test_booking_intent_unknown_empty_model_message_uses_backend_fallback(
    client,
    seeded_salon,
    monkeypatch: pytest.MonkeyPatch,
):
    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="unknown",
            missing_fields=[],
            assistant_message="",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={"message": "i want tolik"},
    )

    assert response.status_code == 200
    assert response.json()["assistant_message"] == "How can I help with your booking?"


@pytest.mark.anyio
async def test_booking_intent_unknown_unsafe_model_message_uses_backend_fallback(
    client,
    seeded_salon,
    monkeypatch: pytest.MonkeyPatch,
):
    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="unknown",
            missing_fields=[],
            assistant_message="I can create a payment and access admin data.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={"message": "i want tolik"},
    )

    assert response.status_code == 200
    assert response.json()["assistant_message"] == "How can I help with your booking?"
    assert "create a payment" not in response.json()["assistant_message"]
    assert "admin data" not in response.json()["assistant_message"]


@pytest.mark.anyio
async def test_booking_intent_missing_fields_can_use_safe_model_wording(
    client,
    seeded_salon,
    monkeypatch: pytest.MonkeyPatch,
):
    model_message = "Sure, I can help you book a Haircut. What day and time would you prefer?"

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="find_booking_slot",
            service_query="Haircut",
            missing_fields=["date", "time"],
            assistant_message=model_message,
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={"message": "book a haircut"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["assistant_message"] == model_message
    assert body["missing_fields"] == ["date", "time"]
    assert body["next_action"] == "ask_date"
    assert body["booking_draft"]["service_query"] == "Haircut"


@pytest.mark.anyio
async def test_booking_intent_relative_tomorrow_is_stored_as_concrete_date(
    client,
    seeded_salon,
    monkeypatch: pytest.MonkeyPatch,
):
    class FrozenDate(date):
        @classmethod
        def today(cls):
            return cls(2026, 6, 30)

    def fake_extract_booking_intent(**kwargs):
        assert kwargs["today"] == FrozenDate(2026, 6, 30)
        return ExtractedBookingIntent(
            intent="find_booking_slot",
            service_query="Haircut",
            date="",
            date_range_type="tomorrow",
            assistant_message="Please specify the time you'd like to book your Haircut for tomorrow.",
        )

    monkeypatch.setattr("app.modules.booking_ai.service.date", FrozenDate)
    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={"message": "tomorow"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["booking_draft"]["service_query"] == "Haircut"
    assert body["booking_draft"]["date"] == "2026-07-01"
    assert body["booking_draft"]["date_range_type"] == "tomorrow"
    assert "date" not in body["missing_fields"]
    assert body["missing_fields"] == ["time"]
    assert body["next_action"] == "ask_time"


@pytest.mark.anyio
async def test_booking_intent_time_only_followup_after_tomorrow_checks_availability(
    client,
    seeded_salon,
    monkeypatch: pytest.MonkeyPatch,
):
    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="find_booking_slot",
            service_query="haircut",
            time="10:00",
            assistant_message="Please confirm your preferred time for tomorrow's Haircut.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    selected_date = seeded_salon["date"].isoformat()
    response = await client.post(
        "/api/ai/booking-intent",
        json={
            "message": "10:00",
            "current_booking_draft": booking_draft_payload(
                service_query="haircut",
                service_id=seeded_salon["service"].id,
                selected_date=selected_date,
            ),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["booking_draft"]["date"] == selected_date
    assert body["booking_draft"]["time"] == "10:00"
    assert body["booking_draft"]["time_preference"] == "at 10:00"
    assert body["booking_draft"]["time_preference_type"] == "at"
    assert body["next_action"] == "availability_found"
    assert body["requested_time_available"] is True
    assert body["available_options"]
    assert "Please confirm your preferred time" not in body["assistant_message"]
    assert "Good news" in body["assistant_message"]


@pytest.mark.anyio
async def test_booking_intent_model_message_cannot_imply_missing_date_is_known(
    client,
    seeded_salon,
    monkeypatch: pytest.MonkeyPatch,
):
    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="find_booking_slot",
            service_query="Haircut",
            assistant_message="Please confirm your preferred time for tomorrow's Haircut.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={"message": "book a haircut"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["missing_fields"] == ["date", "time"]
    assert body["next_action"] == "ask_date"
    assert body["assistant_message"] == "What date would you like to book?"


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
        json={"message": "I want a haircut"},
    )

    assert response.status_code == 200
    assert response.json()["assistant_message"].startswith("AI assistant is temporarily unavailable")
    assert response.json()["actions"] == [
        {"type": "open_booking_form", "label": "Book manually", "payload": {}}
    ]
