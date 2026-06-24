import pytest

from app.ai.schemas import ExtractedBookingIntent
from app.modules.booking_ai.service_matching import match_public_services_by_name
from tests.booking_ai_helpers import seed_ai_services


def test_service_matching_exact_and_partial_matches_active_names(db_session):
    services_by_name = seed_ai_services(db_session)
    active_services = [
        services_by_name["haircut"],
        services_by_name["beard"],
        services_by_name["combo"],
    ]

    assert match_public_services_by_name(active_services, "haircut") == [
        services_by_name["haircut"]
    ]
    assert match_public_services_by_name(active_services, "BEARD") == [
        services_by_name["beard"],
        services_by_name["combo"],
    ]
    assert match_public_services_by_name(active_services, "dragon haircut") == []


@pytest.mark.anyio
async def test_booking_intent_check_unknown_service_asks_for_valid_service(
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

    response = await client.post(
        "/api/ai/booking-intent",
        json={
            "message": "check",
            "current_booking_draft": {
                "service_query": "dragon shave",
                "date": seeded_salon["date"].isoformat(),
                "time": "10:00",
                "time_preference": "at 10:00",
                "time_preference_type": "at",
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["next_action"] == "ask_service"
    assert "What service are you looking for?" in response.json()["assistant_message"]


@pytest.mark.anyio
async def test_booking_intent_list_services_returns_active_public_services(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    seed_ai_services(db_session)

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="list_services",
            service_query=None,
            missing_fields=[],
            assistant_message="Invented service list",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={"message": "what services do you have?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "list_services"
    assert body["next_action"] == "none"
    assert body["actions"] == []
    assert [service["name"] for service in body["services"]] == [
        "Haircut",
        "Beard Trim",
        "Haircut + Beard",
    ]
    assert "Dragon Haircut" not in body["assistant_message"]
    assert "Haircut - 30 min - €25" in body["assistant_message"]
    assert "Beard Trim - 20 min - €15" in body["assistant_message"]
    assert "Haircut + Beard - 50 min - €35" in body["assistant_message"]
    assert "Invented service list" not in body["assistant_message"]


@pytest.mark.anyio
async def test_booking_intent_service_info_returns_real_price_and_duration(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    seed_ai_services(db_session)

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="service_info",
            service_query="haircut",
            missing_fields=[],
            assistant_message="Haircut is free and takes 5 minutes.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={"message": "how much is haircut?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "service_info"
    assert body["service_query"] == "Haircut"
    assert "Haircut costs €25" in body["assistant_message"]
    assert "takes about 30 minutes" in body["assistant_message"]
    assert "free" not in body["assistant_message"]
    assert "5 minutes" not in body["assistant_message"]


@pytest.mark.anyio
async def test_booking_intent_unknown_service_lists_available_services(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    seed_ai_services(db_session)

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="service_info",
            service_query="dragon haircut",
            missing_fields=[],
            assistant_message="Dragon Haircut costs €99.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={"message": "do you have dragon haircut?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "I couldn't find that service" in body["assistant_message"]
    assert "Available services are: Haircut, Beard Trim, Haircut + Beard" in body["assistant_message"]
    assert "Dragon Haircut" not in body["assistant_message"]


@pytest.mark.anyio
async def test_booking_intent_ambiguous_service_info_asks_to_clarify(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    seed_ai_services(db_session)

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="service_info",
            service_query="beard",
            missing_fields=[],
            assistant_message="Beard details.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={"message": "tell me about beard"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "Which one do you mean?" in body["assistant_message"]
    assert [service["name"] for service in body["services"]] == [
        "Beard Trim",
        "Haircut + Beard",
    ]
