from datetime import date

import pytest

from app.ai.schemas import CurrentBookingDraft, ExtractedBookingIntent
from app.modules.booking_ai.draft import merge_booking_draft
from tests.booking_ai_helpers import booking_draft_payload


def test_merge_booking_draft_empty_values_do_not_erase_useful_draft():
    draft = CurrentBookingDraft(
        service_query="Haircut",
        date="2026-06-24",
        time="15:00",
        time_preference="at 15:00",
        time_preference_type="at",
    )
    extracted = ExtractedBookingIntent(
        intent="unknown",
        service_query="",
        date="",
        time="",
        time_preference="",
        time_preference_type="",
        master_preference="",
        missing_fields=[],
        assistant_message="Yes.",
    )

    merged = merge_booking_draft(draft, extracted)

    assert merged == draft


@pytest.mark.anyio
async def test_booking_intent_existing_draft_yes_keeps_details(
    client,
    seeded_salon,
    monkeypatch: pytest.MonkeyPatch,
):
    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="unknown",
            service_query=None,
            date=None,
            time_preference=None,
            master_preference=None,
            missing_fields=[],
            assistant_message="Yes.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )
    selected_date = date.today().isoformat()

    response = await client.post(
        "/api/ai/booking-intent",
        json={
            "message": "yes",
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
    assert response.json()["booking_draft"] == booking_draft_payload(
        service_query="Classic Cut",
        service_id=seeded_salon["service"].id,
        selected_date=selected_date,
        time="15:00",
        time_preference="at 15:00",
        time_preference_type="at",
    )
    assert response.json()["next_action"] in {"availability_alternatives", "ready_to_check_availability"}
    assert "What service" not in response.json()["assistant_message"]
    assert "What date" not in response.json()["assistant_message"]
    assert "What time" not in response.json()["assistant_message"]


@pytest.mark.anyio
async def test_booking_intent_existing_draft_so_keeps_details(
    client,
    seeded_salon,
    monkeypatch: pytest.MonkeyPatch,
):
    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="unknown",
            service_query=None,
            date=None,
            time_preference=None,
            master_preference=None,
            missing_fields=[],
            assistant_message="So...",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )
    selected_date = date.today().isoformat()

    response = await client.post(
        "/api/ai/booking-intent",
        json={
            "message": "so",
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
