from decimal import Decimal

from app.modules.services.models import Service


def booking_draft_payload(
    *,
    service_query: str | None = None,
    service_id: int | None = None,
    selected_date: str | None = None,
    time: str | None = None,
    time_preference: str | None = None,
    time_preference_type: str | None = None,
    master_preference: str | None = None,
    master_id: int | None = None,
    master_name: str | None = None,
) -> dict[str, object]:
    return {
        "service_query": service_query,
        "service_id": service_id,
        "date": selected_date,
        "time": time,
        "time_preference": time_preference,
        "time_preference_type": time_preference_type,
        "master_preference": master_preference,
        "master_id": master_id,
        "master_name": master_name,
    }


def seed_ai_services(db_session):
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
        description="Beard shaping and trim",
        duration_minutes=20,
        cleanup_time_minutes=0,
        price=Decimal("15.00"),
        is_active=True,
        sort_order=2,
    )
    combo = Service(
        name="Haircut + Beard",
        description="Haircut and beard trim",
        duration_minutes=50,
        cleanup_time_minutes=0,
        price=Decimal("35.00"),
        is_active=True,
        sort_order=3,
    )
    inactive = Service(
        name="Dragon Haircut",
        description="Inactive service",
        duration_minutes=60,
        cleanup_time_minutes=0,
        price=Decimal("99.00"),
        is_active=False,
        sort_order=4,
    )
    db_session.add_all([haircut, beard, combo, inactive])
    db_session.commit()
    return {
        "haircut": haircut,
        "beard": beard,
        "combo": combo,
        "inactive": inactive,
    }
