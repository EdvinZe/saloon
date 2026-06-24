import pytest

from app.ai.schemas import ExtractedBookingIntent
from tests.booking_ai_helpers import booking_draft_payload


@pytest.mark.anyio
async def test_booking_intent_available_slot_returns_prefill_booking_action(
    client,
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
    assert response.json()["actions"] == [
        {
            "type": "prefill_booking",
            "label": "Continue booking",
            "payload": {
                "service_id": service.id,
                "master_id": master.id,
                "date": selected_date.isoformat(),
                "time": "10:00",
            },
        }
    ]
    assert all(action["type"] != "payment" for action in response.json()["actions"])


@pytest.mark.anyio
async def test_booking_intent_nearest_options_return_prefill_actions(
    client,
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
    assert body["actions"]
    assert body["actions"][0]["type"] == "prefill_booking"
    assert body["actions"][0]["label"] == "Use 11:30"
    assert body["actions"][0]["payload"]["service_id"] == seeded_salon["service"].id
    assert body["actions"][0]["payload"]["date"] == selected_date.isoformat()
    assert body["actions"][0]["payload"]["time"] == "11:30"
    assert all(action["type"] != "payment" for action in body["actions"])
