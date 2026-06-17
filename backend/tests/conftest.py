import os
from collections.abc import Iterator
from datetime import date, time, timedelta
from decimal import Decimal

import pytest
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

os.environ.setdefault("AUTO_CREATE_TABLES", "false")
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("LOG_LEVEL", "WARNING")
os.environ.setdefault("STRIPE_SECRET_KEY", "sk_test_placeholder")
os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "whsec_placeholder")

from app.core.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.modules.bookings.models import Booking  # noqa: E402
from app.modules.master_shifts.models import MasterShift  # noqa: E402
from app.modules.masters.models import Master, MasterService  # noqa: E402
from app.modules.services.models import Service  # noqa: E402


@pytest.fixture()
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture()
def testing_session_local(tmp_path, monkeypatch: pytest.MonkeyPatch) -> Iterator[sessionmaker[Session]]:
    database_url = f"sqlite:///{tmp_path / 'test.db'}"
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)

    monkeypatch.setattr(
        "app.modules.bookings.service.notify_new_same_day_booking",
        lambda booking: None,
    )
    monkeypatch.setattr(
        "app.modules.notifications.booking_emails.send_email",
        lambda **kwargs: True,
    )
    monkeypatch.setattr(
        "app.modules.payments.confirmation_service.send_booking_confirmation_email",
        lambda booking: None,
    )

    try:
        yield TestingSessionLocal
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def db_session(testing_session_local: sessionmaker[Session]) -> Iterator[Session]:
    db = testing_session_local()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
async def client(testing_session_local: sessionmaker[Session]):
    async def run_sync_inline(func, *args, **kwargs):
        return func(*args, **kwargs)

    async def override_get_db() -> Iterator[Session]:
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    import fastapi.routing

    original_run_in_threadpool = fastapi.routing.run_in_threadpool
    fastapi.routing.run_in_threadpool = run_sync_inline
    app.dependency_overrides[get_db] = override_get_db
    transport = httpx.ASGITransport(app=app)
    try:
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        fastapi.routing.run_in_threadpool = original_run_in_threadpool


@pytest.fixture()
def seeded_salon(db_session: Session) -> dict[str, object]:
    service = Service(
        name="Classic Cut",
        description="Haircut",
        duration_minutes=30,
        cleanup_time_minutes=0,
        price=Decimal("25.00"),
        is_active=True,
        sort_order=1,
    )
    master = Master(
        first_name="Alex",
        last_name="Barber",
        role="Senior Barber",
        bio="",
        initials="AB",
        is_active=True,
        sort_order=1,
    )
    db_session.add_all([service, master])
    db_session.flush()
    db_session.add(MasterService(master_id=master.id, service_id=service.id))

    selected_date = date.today() + timedelta(days=7)
    db_session.add(
        MasterShift(
            shift_code=f"shift-{master.id}-{selected_date.isoformat()}",
            master_id=master.id,
            date=selected_date,
            start_time=time(10, 0),
            end_time=time(12, 0),
            status="working",
        )
    )
    db_session.commit()

    return {
        "service": service,
        "master": master,
        "date": selected_date,
        "time": "10:00",
    }


def booking_payload(seeded_salon: dict[str, object]) -> dict[str, object]:
    service = seeded_salon["service"]
    master = seeded_salon["master"]
    selected_date = seeded_salon["date"]
    assert isinstance(service, Service)
    assert isinstance(master, Master)
    assert isinstance(selected_date, date)

    return {
        "service_id": service.id,
        "master_id": master.id,
        "date": selected_date.isoformat(),
        "time": str(seeded_salon["time"]),
        "customer_first_name": "Jamie",
        "customer_last_name": "Client",
        "customer_phone": "+37060000000",
        "customer_email": "jamie@example.com",
    }


def create_booking(
    db_session: Session,
    seeded_salon: dict[str, object],
    *,
    payment_intent_id: str = "pi_test_existing",
) -> Booking:
    from app.modules.bookings.schemas import BookingCreate
    from app.modules.bookings.service import create_confirmed_booking

    booking = create_confirmed_booking(
        db=db_session,
        data=BookingCreate(**booking_payload(seeded_salon)),
        source="online",
        stripe_payment_intent_id=payment_intent_id,
    )
    db_session.refresh(booking)
    return booking
