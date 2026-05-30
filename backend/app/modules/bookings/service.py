import logging
import re
import secrets
from datetime import date, datetime, time, timedelta

from fastapi import HTTPException, status as http_status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.bookings.models import Booking
from app.modules.bookings.schemas import BookingAvailabilityCheckResponse, BookingCreate
from app.modules.master_shifts.models import MasterShift
from app.modules.masters.models import Master, MasterService
from app.modules.services.models import Service
from app.modules.services.service import get_service_total_duration_minutes

logger = logging.getLogger(__name__)

VALID_BOOKING_STATUSES = {"confirmed", "cancelled", "completed", "no_show"}
VALID_DEPOSIT_STATUSES = {"paid", "refunded", "retained"}
VALID_SOURCES = {"online", "manager_panel", "telegram_bot"}
BLOCKING_BOOKING_STATUSES = ("confirmed",)
AVAILABLE_SHIFT_STATUSES = ("working", "extra_day")


def generate_manage_token() -> str:
    return secrets.token_urlsafe(32)


def generate_booking_code(booking: Booking, master: Master) -> str:
    customer_initials = (
        f"{booking.customer_first_name[:1]}{booking.customer_last_name[:1]}"
    ).upper()
    return (
        f"BK-{booking.start_at:%Y%m%d}-{master.initials.upper()}-"
        f"{customer_initials}-S{booking.service_id}-{booking.id:04d}"
    )


def parse_booking_start(selected_date: date, time_str: str) -> datetime:
    if re.fullmatch(r"\d{2}:\d{2}", time_str) is None:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="time must be in HH:MM format",
        )

    try:
        selected_time = datetime.strptime(time_str, "%H:%M").time()
    except ValueError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="time must be in HH:MM format",
        ) from exc

    return datetime.combine(selected_date, selected_time)


def validate_booking_creation(
    db: Session,
    data: BookingCreate,
) -> tuple[Service, Master, datetime, datetime]:
    service = db.get(Service, data.service_id)
    if service is None or not service.is_active:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Active service not found: {data.service_id}",
        )

    master = db.get(Master, data.master_id)
    if master is None or not master.is_active:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Active master not found: {data.master_id}",
        )

    master_service_exists = db.scalar(
        select(MasterService.id).where(
            MasterService.master_id == data.master_id,
            MasterService.service_id == data.service_id,
        )
    )
    if master_service_exists is None:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Selected master cannot perform selected service",
        )

    start_at = parse_booking_start(data.date, data.time)
    if start_at < datetime.now():
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Cannot book a time in the past",
        )

    end_at = start_at + timedelta(minutes=get_service_total_duration_minutes(service))

    shifts = list(
        db.scalars(
            select(MasterShift).where(
                MasterShift.master_id == data.master_id,
                MasterShift.date == data.date,
                MasterShift.status.in_(AVAILABLE_SHIFT_STATUSES),
            )
        ).all()
    )
    if not shifts:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Selected master has no working shift for selected date",
        )

    if not _fits_any_shift(shifts, data.date, start_at, end_at):
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Selected time does not fit master's working shift",
        )

    if has_overlapping_confirmed_booking(db, data.master_id, start_at, end_at):
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail="Selected slot is already taken",
        )

    return service, master, start_at, end_at


def create_confirmed_booking(
    db: Session,
    data: BookingCreate,
    source: str = "online",
    deposit_amount_cents: int = 1000,
    currency: str = "EUR",
    stripe_checkout_session_id: str | None = None,
    stripe_payment_intent_id: str | None = None,
) -> Booking:
    if source not in VALID_SOURCES:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid booking source: {source}",
        )

    if stripe_payment_intent_id is not None:
        existing_booking = db.scalar(
            select(Booking).where(
                Booking.stripe_payment_intent_id == stripe_payment_intent_id
            )
        )
        if existing_booking is not None:
            return existing_booking

    _, master, start_at, end_at = validate_booking_creation(db, data)
    booking = Booking(
        service_id=data.service_id,
        master_id=data.master_id,
        customer_first_name=data.customer_first_name,
        customer_last_name=data.customer_last_name,
        customer_phone=data.customer_phone,
        customer_email=str(data.customer_email),
        start_at=start_at,
        end_at=end_at,
        status="confirmed",
        deposit_status="paid",
        source=source,
        deposit_amount_cents=deposit_amount_cents,
        currency=currency,
        stripe_checkout_session_id=stripe_checkout_session_id,
        stripe_payment_intent_id=stripe_payment_intent_id,
        manage_token=generate_manage_token(),
    )

    db.add(booking)
    db.flush()
    booking.booking_code = generate_booking_code(booking, master)
    db.commit()
    db.refresh(booking)

    logger.info(
        "[BOOKINGS] Booking created: booking_id=%s booking_code=%s source=%s",
        booking.id,
        booking.booking_code,
        booking.source,
    )

    return booking


def check_booking_availability(
    db: Session,
    data: BookingCreate,
) -> BookingAvailabilityCheckResponse:
    validate_booking_creation(db, data)

    logger.info(
        "[BOOKINGS] Booking availability checked: service_id=%s master_id=%s "
        "date=%s time=%s",
        data.service_id,
        data.master_id,
        data.date,
        data.time,
    )

    return BookingAvailabilityCheckResponse(
        available=True,
        message="Selected slot is available",
    )


def list_bookings(
    db: Session,
    status: str | None = None,
    source: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[Booking]:
    statement = select(Booking)

    if status is not None:
        if status not in VALID_BOOKING_STATUSES:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid booking status: {status}",
            )
        statement = statement.where(Booking.status == status)

    if source is not None:
        if source not in VALID_SOURCES:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid booking source: {source}",
            )
        statement = statement.where(Booking.source == source)

    if start_date is not None:
        statement = statement.where(
            Booking.start_at >= datetime.combine(start_date, time.min)
        )

    if end_date is not None:
        statement = statement.where(
            Booking.start_at <= datetime.combine(end_date, time.max)
        )

    statement = statement.order_by(Booking.start_at.desc(), Booking.id.desc())
    return list(db.scalars(statement).all())


def get_booking_by_manage_token(db: Session, token: str) -> Booking | None:
    if not token or not token.strip():
        return None

    return db.scalar(select(Booking).where(Booking.manage_token == token.strip()))


def cancel_booking_by_manage_token(db: Session, token: str) -> Booking:
    cleaned_token = token.strip() if token else ""
    if not cleaned_token:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Booking token is required",
        )

    booking = get_booking_by_manage_token(db, cleaned_token)
    if booking is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    if booking.status == "cancelled":
        return booking

    if booking.status in ("completed", "no_show"):
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Booking can no longer be cancelled",
        )

    if booking.status != "confirmed":
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Booking cannot be cancelled",
        )

    booking.status = "cancelled"
    # TODO: Integrate Stripe refunds separately from booking cancellation.
    db.commit()
    db.refresh(booking)

    logger.info(
        "[BOOKINGS] Booking cancelled: booking_id=%s booking_code=%s",
        booking.id,
        booking.booking_code,
    )

    return booking


def get_booking_by_payment_intent(
    db: Session,
    payment_intent_id: str,
) -> Booking | None:
    if not payment_intent_id or not payment_intent_id.strip():
        return None

    return db.scalar(
        select(Booking).where(
            Booking.stripe_payment_intent_id == payment_intent_id.strip()
        )
    )


def has_overlapping_confirmed_booking(
    db: Session,
    master_id: int,
    start_at: datetime,
    end_at: datetime,
) -> bool:
    existing_booking_id = db.scalar(
        select(Booking.id).where(
            Booking.master_id == master_id,
            Booking.status.in_(BLOCKING_BOOKING_STATUSES),
            Booking.start_at < end_at,
            Booking.end_at > start_at,
        )
    )
    return existing_booking_id is not None


def _fits_any_shift(
    shifts: list[MasterShift],
    selected_date: date,
    start_at: datetime,
    end_at: datetime,
) -> bool:
    for shift in shifts:
        if shift.start_time is None or shift.end_time is None:
            continue

        shift_start = datetime.combine(selected_date, shift.start_time)
        shift_end = datetime.combine(selected_date, shift.end_time)

        if start_at >= shift_start and end_at <= shift_end:
            return True

    return False
