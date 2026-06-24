from decimal import Decimal

from app.modules.masters.models import Master, MasterService
from app.modules.services.models import Service


def booking_draft_payload(
    *,
    service_query: str | None = None,
    service_id: int | None = None,
    master_query: str | None = None,
    selected_date: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    date_range_type: str | None = None,
    weekdays: list[str] | None = None,
    time: str | None = None,
    end_time: str | None = None,
    time_preference: str | None = None,
    time_preference_type: str | None = None,
    daypart: str | None = None,
    limit: int | None = None,
    master_preference: str | None = None,
    master_id: int | None = None,
    master_name: str | None = None,
) -> dict[str, object]:
    return {
        "service_query": service_query,
        "service_id": service_id,
        "master_query": master_query,
        "date": selected_date,
        "start_date": start_date,
        "end_date": end_date,
        "date_range_type": date_range_type,
        "weekdays": weekdays,
        "time": time,
        "end_time": end_time,
        "time_preference": time_preference,
        "time_preference_type": time_preference_type,
        "daypart": daypart,
        "limit": limit,
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


def seed_ai_masters(db_session):
    services = seed_ai_services(db_session)
    alex = Master(
        first_name="Alex",
        last_name="Kravtsov",
        role="Senior Barber",
        bio="Sharp fades and classic cuts.",
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
    john = Master(
        first_name="John",
        last_name="Reed",
        role="Barber",
        bio="",
        initials="JR",
        is_active=True,
        sort_order=3,
    )
    inactive = Master(
        first_name="Hidden",
        last_name="Master",
        role="Admin Only",
        bio="Private",
        initials="HM",
        is_active=False,
        sort_order=4,
    )
    db_session.add_all([alex, maria, john, inactive])
    db_session.flush()
    db_session.add_all([
        MasterService(master_id=alex.id, service_id=services["haircut"].id),
        MasterService(master_id=alex.id, service_id=services["beard"].id),
        MasterService(master_id=maria.id, service_id=services["haircut"].id),
        MasterService(master_id=john.id, service_id=services["beard"].id),
        MasterService(master_id=inactive.id, service_id=services["haircut"].id),
    ])
    db_session.commit()
    return {
        **services,
        "alex": alex,
        "maria": maria,
        "john": john,
        "inactive_master": inactive,
    }
