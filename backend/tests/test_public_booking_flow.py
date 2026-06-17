import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from tests.conftest import booking_payload, create_booking


pytestmark = pytest.mark.anyio


async def test_public_services_and_masters_return_seeded_data(
    client: AsyncClient,
    seeded_salon,
):
    services_response = await client.get("/api/services/public")
    masters_response = await client.get("/api/masters/public")

    assert services_response.status_code == 200
    assert masters_response.status_code == 200
    assert services_response.json()[0]["name"] == "Classic Cut"
    assert masters_response.json()[0]["name"] == "Alex Barber"


async def test_availability_endpoints_return_slots_and_available_masters(
    client: AsyncClient,
    seeded_salon,
):
    payload = booking_payload(seeded_salon)

    slots_response = await client.get(
        "/api/availability/slots",
        params={
            "service_id": payload["service_id"],
            "date": payload["date"],
        },
    )
    masters_response = await client.get(
        "/api/availability/masters",
        params={
            "service_id": payload["service_id"],
            "date": payload["date"],
            "time": payload["time"],
        },
    )

    assert slots_response.status_code == 200
    assert {"time": "10:00", "status": "free"} in slots_response.json()
    assert masters_response.status_code == 200
    assert masters_response.json()[0]["name"] == "Alex Barber"


async def test_booking_availability_rejects_existing_confirmed_booking(
    client: AsyncClient,
    db_session: Session,
    seeded_salon,
):
    payload = booking_payload(seeded_salon)

    free_response = await client.post("/api/bookings/check-availability", json=payload)
    assert free_response.status_code == 200
    assert free_response.json()["available"] is True

    create_booking(db_session, seeded_salon)

    conflict_response = await client.post(
        "/api/bookings/check-availability",
        json=payload,
    )
    assert conflict_response.status_code == 409
    assert conflict_response.json()["detail"] == "Selected slot is already taken"
