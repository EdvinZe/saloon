import re
from datetime import date, datetime, time, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.availability.schemas import AvailableSlotStatus
from app.modules.bookings.models import Booking
from app.modules.master_shifts.models import MasterShift
from app.modules.masters.models import Master, MasterService
from app.modules.services.models import Service
from app.modules.services.service import get_service_total_duration_minutes

AVAILABLE_SHIFT_STATUSES = ("working", "extra_day")
BLOCKING_BOOKING_STATUSES = ("confirmed",)
SLOT_STEP_MINUTES = 15


def list_available_slots(
    db: Session,
    service_id: int,
    selected_date: date,
) -> list[AvailableSlotStatus]:
    service = _get_active_service_or_404(db, service_id)
    total_duration = get_service_total_duration_minutes(service)
    master_ids = _get_active_master_ids_for_service(db, service_id)
    now = datetime.now()

    if not master_ids:
        return []

    shifts = _get_available_shifts_for_masters(db, master_ids, selected_date)
    slot_statuses: dict[str, str] = {}

    for shift in shifts:
        if shift.start_time is None or shift.end_time is None:
            continue

        shift_start = _combine(selected_date, shift.start_time)
        shift_end = _combine(selected_date, shift.end_time)
        current = shift_start

        while current < shift_end:
            if current < now:
                current += timedelta(minutes=SLOT_STEP_MINUTES)
                continue

            slot_end = current + timedelta(minutes=total_duration)
            time_key = current.strftime("%H:%M")
            status_value = "tooShort"

            if slot_end <= shift_end and not _master_has_booking_conflict(
                db,
                shift.master_id,
                current,
                slot_end,
            ):
                status_value = "free"

            if slot_statuses.get(time_key) != "free":
                slot_statuses[time_key] = status_value

            current += timedelta(minutes=SLOT_STEP_MINUTES)

    return [
        AvailableSlotStatus(time=slot_time, status=slot_statuses[slot_time])
        for slot_time in sorted(slot_statuses)
    ]


def list_available_masters(
    db: Session,
    service_id: int,
    selected_date: date,
    selected_time: str,
) -> list[Master]:
    service = _get_active_service_or_404(db, service_id)
    total_duration = get_service_total_duration_minutes(service)
    slot_start_time = _parse_slot_time(selected_time)
    slot_start = _combine(selected_date, slot_start_time)
    if slot_start < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot check availability for a time in the past",
        )

    slot_end = slot_start + timedelta(minutes=total_duration)

    statement = (
        select(Master)
        .join(MasterService)
        .where(
            Master.is_active.is_(True),
            MasterService.service_id == service_id,
        )
        .options(selectinload(Master.service_links).selectinload(MasterService.service))
        .order_by(Master.sort_order, Master.id)
    )
    masters = list(db.scalars(statement).unique().all())

    if not masters:
        return []

    master_ids = [master.id for master in masters]
    shifts_by_master: dict[int, list[MasterShift]] = {}
    for shift in _get_available_shifts_for_masters(db, master_ids, selected_date):
        shifts_by_master.setdefault(shift.master_id, []).append(shift)

    return [
        master
        for master in masters
        if _master_has_fitting_shift(
            shifts_by_master.get(master.id, []),
            selected_date,
            slot_start,
            slot_end,
        )
        and not _master_has_booking_conflict(db, master.id, slot_start, slot_end)
    ]


def _get_active_service_or_404(db: Session, service_id: int) -> Service:
    service = db.get(Service, service_id)
    if service is None or not service.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Active service not found: {service_id}",
        )

    return service


def _get_active_master_ids_for_service(db: Session, service_id: int) -> list[int]:
    statement = (
        select(Master.id)
        .join(MasterService)
        .where(
            Master.is_active.is_(True),
            MasterService.service_id == service_id,
        )
        .order_by(Master.sort_order, Master.id)
    )
    return list(db.scalars(statement).all())


def _get_available_shifts_for_masters(
    db: Session,
    master_ids: list[int],
    selected_date: date,
) -> list[MasterShift]:
    statement = (
        select(MasterShift)
        .where(
            MasterShift.master_id.in_(master_ids),
            MasterShift.date == selected_date,
            MasterShift.status.in_(AVAILABLE_SHIFT_STATUSES),
        )
        .order_by(MasterShift.start_time, MasterShift.id)
    )
    return list(db.scalars(statement).all())


def _parse_slot_time(value: str) -> time:
    if re.fullmatch(r"\d{2}:\d{2}", value) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="time must be in HH:MM format",
        )

    try:
        return datetime.strptime(value, "%H:%M").time()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="time must be in HH:MM format",
        ) from exc


def _master_has_fitting_shift(
    shifts: list[MasterShift],
    selected_date: date,
    slot_start: datetime,
    slot_end: datetime,
) -> bool:
    for shift in shifts:
        if shift.start_time is None or shift.end_time is None:
            continue

        shift_start = _combine(selected_date, shift.start_time)
        shift_end = _combine(selected_date, shift.end_time)

        if slot_start >= shift_start and slot_end <= shift_end:
            return True

    return False


def _master_has_booking_conflict(
    db: Session,
    master_id: int,
    slot_start: datetime,
    slot_end: datetime,
) -> bool:
    booking_id = db.scalar(
        select(Booking.id).where(
            Booking.master_id == master_id,
            Booking.status.in_(BLOCKING_BOOKING_STATUSES),
            Booking.start_at < slot_end,
            Booking.end_at > slot_start,
        )
    )
    return booking_id is not None


def _combine(value_date: date, value_time: time) -> datetime:
    return datetime.combine(value_date, value_time)
