from datetime import date, time, timedelta
from decimal import Decimal

import pytest

from app.ai.schemas import ExtractedBookingIntent
from app.modules.bookings.models import Booking
from app.modules.master_shifts.models import MasterShift
from app.modules.masters.models import Master, MasterService
from app.modules.services.models import Service
from tests.booking_ai_helpers import booking_draft_payload


def seed_flexible_salon(db_session):
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
        description="Beard shaping",
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
    maria = Master(
        first_name="Maria",
        last_name="Stone",
        role="Hair Stylist",
        bio="",
        initials="MS",
        is_active=True,
        sort_order=2,
    )
    db_session.add_all([haircut, beard, alex, maria])
    db_session.flush()
    db_session.add_all([
        MasterService(master_id=alex.id, service_id=haircut.id),
        MasterService(master_id=alex.id, service_id=beard.id),
        MasterService(master_id=maria.id, service_id=haircut.id),
    ])

    today = date.today()
    tomorrow = today + timedelta(days=1)
    after_tomorrow = today + timedelta(days=2)
    next_week = today + timedelta(days=7)
    shifts = [
        (alex, today, time(17, 30), time(19, 0)),
        (maria, after_tomorrow, time(18, 0), time(19, 0)),
        (alex, tomorrow, time(13, 0), time(15, 0)),
        (alex, next_week, time(10, 0), time(11, 0)),
    ]
    for master, shift_date, start_time, end_time in shifts:
        db_session.add(
            MasterShift(
                shift_code=f"flex-{master.id}-{shift_date.isoformat()}-{start_time.isoformat()}",
                master_id=master.id,
                date=shift_date,
                start_time=start_time,
                end_time=end_time,
                status="working",
            )
        )
    db_session.commit()
    return {
        "haircut": haircut,
        "beard": beard,
        "alex": alex,
        "maria": maria,
        "today": today,
        "tomorrow": tomorrow,
        "after_tomorrow": after_tomorrow,
        "next_week": next_week,
    }


@pytest.mark.anyio
async def test_flexible_availability_missing_service_asks_for_service(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    seed_flexible_salon(db_session)

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="flexible_availability_search",
            date_range_type="this_week",
            time_preference_type="after",
            time="17:00",
            missing_fields=[],
            assistant_message="I found many.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={"message": "anything after 17:00 this week?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "flexible_availability_search"
    assert body["next_action"] == "ask_service"
    assert body["assistant_message"] == "What service are you looking for?"
    assert body["available_options"] == []
    assert body["actions"] == []
    assert body["booking_draft"]["date_range_type"] == "this_week"
    assert body["booking_draft"]["time"] == "17:00"


@pytest.mark.anyio
async def test_flexible_availability_context_continuation_searches_previous_criteria(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    data = seed_flexible_salon(db_session)

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="find_booking_slot",
            service_query="haircut",
            missing_fields=[],
            assistant_message="Haircut.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={
            "message": "haircut",
            "current_booking_draft": booking_draft_payload(
                selected_date=None,
                service_query=None,
                time="17:00",
                time_preference="after 17:00",
                time_preference_type="after",
            )
            | {
                "date_range_type": "this_week",
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "flexible_availability_search"
    assert body["next_action"] == "availability_options_found"
    assert body["available_options"][0]["service_id"] == data["haircut"].id
    assert body["available_options"][0]["date"] == data["today"].isoformat()
    assert body["available_options"][0]["time"] == "17:30"


@pytest.mark.anyio
async def test_flexible_availability_weekdays_after_time_returns_real_options(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    seed_flexible_salon(db_session)

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="flexible_availability_search",
            service_query="haircut",
            date_range_type="weekdays",
            weekdays=["monday", "tuesday", "wednesday", "thursday", "friday"],
            time_preference_type="after",
            time="17:00",
            missing_fields=[],
            assistant_message="Invented.",
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
    body = response.json()
    assert body["next_action"] == "availability_options_found"
    assert body["available_options"]
    assert all(option["time"] >= "17:00" for option in body["available_options"])
    assert "I found these Haircut slots on weekdays from 17:00" in body["assistant_message"]
    assert "Invented" not in body["assistant_message"]


@pytest.mark.anyio
async def test_flexible_availability_tomorrow_afternoon_filters_by_daypart(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    data = seed_flexible_salon(db_session)

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="flexible_availability_search",
            service_query="haircut",
            date_range_type="tomorrow",
            date=data["tomorrow"].isoformat(),
            daypart="afternoon",
            missing_fields=[],
            assistant_message="Invented.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={"message": "find me a haircut slot tomorrow afternoon"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["available_options"]
    assert body["available_options"][0]["date"] == data["tomorrow"].isoformat()
    assert body["available_options"][0]["time"] == "13:00"
    assert "tomorrow afternoon" in body["assistant_message"]


@pytest.mark.anyio
async def test_flexible_availability_nearest_slot_returns_earliest_option(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    data = seed_flexible_salon(db_session)

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="flexible_availability_search",
            service_query="haircut",
            date_range_type="nearest",
            time_preference_type="any",
            missing_fields=[],
            assistant_message="Soon.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={"message": "what is the nearest haircut slot?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["available_options"][0]["date"] == data["today"].isoformat()
    assert body["available_options"][0]["time"] == "17:30"


@pytest.mark.anyio
async def test_flexible_availability_actions_match_options(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    seed_flexible_salon(db_session)

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="flexible_availability_search",
            service_query="haircut",
            date_range_type="nearest",
            time_preference_type="any",
            missing_fields=[],
            assistant_message="Soon.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={"message": "what is the nearest haircut slot?"},
    )

    assert response.status_code == 200
    body = response.json()
    prefill_actions = [
        action for action in body["actions"] if action["type"] == "prefill_booking"
    ]
    assert len(prefill_actions) == len(body["available_options"])
    for action, option in zip(prefill_actions, body["available_options"], strict=True):
        assert action["type"] == "prefill_booking"
        assert action["label"].startswith("Use ")
        assert action["payload"] == {
            "service_id": option["service_id"],
            "master_id": option["master_id"],
            "date": option["date"],
            "time": option["time"],
        }


@pytest.mark.anyio
async def test_flexible_availability_no_results_returns_safe_message(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    data = seed_flexible_salon(db_session)

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="flexible_availability_search",
            service_query="beard trim",
            date_range_type="tomorrow",
            date=data["tomorrow"].isoformat(),
            time_preference_type="after",
            time="19:30",
            missing_fields=[],
            assistant_message="Found one.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={"message": "any beard trim tomorrow after 19:30?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["available_options"] == []
    assert [action["type"] for action in body["actions"]] == [
        "open_booking_form",
        "reset_ai_draft",
    ]
    assert "I couldn't find Beard Trim slots tomorrow from 19:30" in body["assistant_message"]
    assert "Found one" not in body["assistant_message"]


@pytest.mark.anyio
async def test_flexible_availability_unknown_service_lists_services(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    seed_flexible_salon(db_session)

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="flexible_availability_search",
            service_query="dragon cut",
            date_range_type="nearest",
            missing_fields=[],
            assistant_message="Dragon Cut at noon.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={"message": "nearest dragon cut"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "I couldn't find that service" in body["assistant_message"]
    assert "Available services are: Haircut, Beard Trim" in body["assistant_message"]
    assert "Dragon Cut at noon" not in body["assistant_message"]


@pytest.mark.anyio
async def test_flexible_availability_optional_master_filters_results(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    data = seed_flexible_salon(db_session)

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="flexible_availability_search",
            service_query="haircut",
            master_query="Alex",
            date_range_type="tomorrow",
            date=data["tomorrow"].isoformat(),
            time_preference_type="after",
            time="12:00",
            missing_fields=[],
            assistant_message="Anything with Alex.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={"message": "anything with Alex after 12:00 tomorrow for haircut"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["master_query"] == "Alex Kravtsov"
    assert body["available_options"]
    assert all(option["master_name"] == "Alex Kravtsov" for option in body["available_options"])


@pytest.mark.anyio
async def test_flexible_availability_does_not_create_booking_or_payment_intent(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    seed_flexible_salon(db_session)
    calls = {"payment_intent": 0}

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="flexible_availability_search",
            service_query="haircut",
            date_range_type="nearest",
            missing_fields=[],
            assistant_message="Soon.",
        )

    def fake_payment_intent(*args, **kwargs):
        calls["payment_intent"] += 1
        raise AssertionError("PaymentIntent must not be created by AI flexible availability")

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )
    monkeypatch.setattr(
        "app.modules.payments.stripe_service.stripe.PaymentIntent.create",
        fake_payment_intent,
    )
    before_count = db_session.query(Booking).count()

    response = await client.post(
        "/api/ai/booking-intent",
        json={"message": "what is the nearest haircut slot?"},
    )

    assert response.status_code == 200
    assert db_session.query(Booking).count() == before_count
    assert calls["payment_intent"] == 0
