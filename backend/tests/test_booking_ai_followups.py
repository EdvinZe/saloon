from datetime import date, time, timedelta
from decimal import Decimal

import pytest

from app.ai.schemas import ExtractedBookingIntent
from app.modules.bookings.models import Booking
from app.modules.master_shifts.models import MasterShift
from app.modules.masters.models import Master, MasterService
from app.modules.services.models import Service


def seed_followup_salon(db_session):
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
        MasterService(master_id=maria.id, service_id=haircut.id),
        MasterService(master_id=alex.id, service_id=beard.id),
    ])

    today = date.today()
    start_date = today + timedelta(days=1)
    end_date = start_date + timedelta(days=3)
    shift_days = [start_date + timedelta(days=offset) for offset in range(4)]
    for shift_day in shift_days:
        db_session.add_all([
            MasterShift(
                shift_code=f"follow-alex-{shift_day.isoformat()}",
                master_id=alex.id,
                date=shift_day,
                start_time=time(17, 0),
                end_time=time(20, 0),
                status="working",
            ),
            MasterShift(
                shift_code=f"follow-maria-{shift_day.isoformat()}",
                master_id=maria.id,
                date=shift_day,
                start_time=time(17, 0),
                end_time=time(20, 0),
                status="working",
            ),
        ])

    db_session.commit()
    return {
        "haircut": haircut,
        "beard": beard,
        "alex": alex,
        "maria": maria,
        "start_date": start_date,
        "end_date": end_date,
    }


@pytest.mark.anyio
async def test_pending_flexible_search_service_answer_runs_search_not_service_info(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    data = seed_followup_salon(db_session)

    def fake_extract_booking_intent(**kwargs):
        if kwargs["user_message"] == "haircut":
            return ExtractedBookingIntent(
                intent="service_info",
                service_query="haircut",
                missing_fields=[],
                assistant_message="Haircut costs €25.",
            )
        return ExtractedBookingIntent(
            intent="flexible_availability_search",
            start_date=data["start_date"].isoformat(),
            end_date=data["end_date"].isoformat(),
            date_range_type="date_range",
            time_preference_type="after",
            time="17:00",
            missing_fields=[],
            assistant_message="Found slots.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    first = await client.post(
        "/api/ai/booking-intent",
        json={"message": "what time do you have from Tuesday to Friday from 17:00"},
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
    assert body["next_action"] == "availability_options_found"
    assert body["available_options"]
    assert "Haircut costs" not in body["assistant_message"]


@pytest.mark.anyio
async def test_pending_flexible_search_partial_service_answer_resolves_service(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    data = seed_followup_salon(db_session)

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="service_info",
            service_query="beard",
            missing_fields=[],
            assistant_message="Beard info.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={
            "message": "beard",
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
    assert response.json()["intent"] == "flexible_availability_search"
    assert response.json()["service_query"] == "Beard Trim"


@pytest.mark.anyio
async def test_show_more_after_flexible_search_returns_next_options(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    seed_followup_salon(db_session)

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="flexible_availability_search",
            service_query="haircut",
            date_range_type="nearest",
            missing_fields=[],
            assistant_message="Slots.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    first = await client.post("/api/ai/booking-intent", json={"message": "nearest haircut"})
    second = await client.post(
        "/api/ai/booking-intent",
        json={
            "message": "show more",
            "current_booking_draft": first.json()["booking_draft"],
        },
    )

    assert second.status_code == 200
    assert second.json()["available_options"]
    assert second.json()["available_options"][0] != first.json()["available_options"][0]
    assert "more Haircut slots" in second.json()["assistant_message"]


@pytest.mark.anyio
async def test_later_after_flexible_search_returns_later_options(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    seed_followup_salon(db_session)

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="flexible_availability_search",
            service_query="haircut",
            date_range_type="nearest",
            missing_fields=[],
            assistant_message="Slots.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    first = await client.post("/api/ai/booking-intent", json={"message": "nearest haircut"})
    later = await client.post(
        "/api/ai/booking-intent",
        json={
            "message": "later",
            "current_booking_draft": first.json()["booking_draft"],
        },
    )

    assert later.status_code == 200
    assert later.json()["available_options"]
    assert later.json()["available_options"][0] != first.json()["available_options"][0]


@pytest.mark.anyio
async def test_earlier_after_flexible_search_returns_safe_message_when_none(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    seed_followup_salon(db_session)

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="flexible_availability_search",
            service_query="haircut",
            date_range_type="nearest",
            missing_fields=[],
            assistant_message="Slots.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    first = await client.post("/api/ai/booking-intent", json={"message": "nearest haircut"})
    earlier = await client.post(
        "/api/ai/booking-intent",
        json={
            "message": "earlier",
            "current_booking_draft": first.json()["booking_draft"],
        },
    )

    assert earlier.status_code == 200
    assert earlier.json()["available_options"] == []
    assert "couldn't find earlier matching slots" in earlier.json()["assistant_message"]


@pytest.mark.anyio
async def test_other_master_after_options_attempts_different_master(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    seed_followup_salon(db_session)

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="flexible_availability_search",
            service_query="haircut",
            date_range_type="nearest",
            missing_fields=[],
            assistant_message="Slots.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    first = await client.post("/api/ai/booking-intent", json={"message": "nearest haircut"})
    other = await client.post(
        "/api/ai/booking-intent",
        json={
            "message": "other master",
            "current_booking_draft": first.json()["booking_draft"],
        },
    )

    assert other.status_code == 200
    assert other.json()["available_options"]
    assert other.json()["available_options"][0]["master_name"] != first.json()["available_options"][0]["master_name"]


@pytest.mark.anyio
async def test_book_manually_returns_open_booking_form_action_without_side_effects(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    seed_followup_salon(db_session)

    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="unknown",
            missing_fields=[],
            assistant_message="Manual.",
        )

    def fake_payment_intent(*args, **kwargs):
        raise AssertionError("PaymentIntent must not be created")

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )
    monkeypatch.setattr(
        "app.modules.payments.stripe_service.stripe.PaymentIntent.create",
        fake_payment_intent,
    )
    before_count = db_session.query(Booking).count()

    response = await client.post("/api/ai/booking-intent", json={"message": "book manually"})

    assert response.status_code == 200
    assert response.json()["actions"] == [
        {"type": "open_booking_form", "label": "Open booking form", "payload": {}}
    ]
    assert db_session.query(Booking).count() == before_count


@pytest.mark.anyio
async def test_start_over_returns_reset_action(
    client,
    seeded_salon,
    monkeypatch: pytest.MonkeyPatch,
):
    def fake_extract_booking_intent(**kwargs):
        return ExtractedBookingIntent(
            intent="unknown",
            missing_fields=[],
            assistant_message="Reset.",
        )

    monkeypatch.setattr(
        "app.modules.booking_ai.service.ai_client.extract_booking_intent",
        fake_extract_booking_intent,
    )

    response = await client.post(
        "/api/ai/booking-intent",
        json={
            "message": "start over",
            "current_booking_draft": {"service_query": "Haircut"},
        },
    )

    assert response.status_code == 200
    assert response.json()["booking_draft"]["service_query"] is None
    assert response.json()["actions"][0]["type"] == "reset_ai_draft"


@pytest.mark.anyio
async def test_service_info_still_works_without_pending_search(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch,
):
    seed_followup_salon(db_session)

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
