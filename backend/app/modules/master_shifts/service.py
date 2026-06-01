import logging
from datetime import date, datetime, timedelta, time

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.master_shifts.models import MasterShift
from app.modules.master_shifts.schemas import (
    AdminScheduleDay,
    AdminScheduleDayUpsert,
    AdminScheduleMaster,
    AdminScheduleRangeResponse,
    AdminScheduleRangeUpsert,
    AdminScheduleResponse,
    MasterShiftCreate,
)
from app.modules.masters.models import Master

logger = logging.getLogger(__name__)

WORKING_STATUSES = {"working", "extra_day"}
UNAVAILABLE_STATUSES = {"day_off", "sick", "vacation", "other"}
ALLOWED_STATUSES = WORKING_STATUSES | UNAVAILABLE_STATUSES


def list_master_shifts(
    db: Session,
    master_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    status: str | None = None,
    search: str | None = None,
) -> list[MasterShift]:
    statement = select(MasterShift)

    if master_id is not None:
        statement = statement.where(MasterShift.master_id == master_id)

    if start_date is not None:
        statement = statement.where(MasterShift.date >= start_date)

    if end_date is not None:
        statement = statement.where(MasterShift.date <= end_date)

    if status is not None:
        statement = statement.where(MasterShift.status == status)

    if search is not None:
        statement = statement.where(MasterShift.shift_code.contains(search))

    statement = statement.order_by(
        MasterShift.date,
        MasterShift.start_time,
        MasterShift.id,
    )
    return list(db.scalars(statement).all())


def create_master_shift(
    db: Session,
    data: MasterShiftCreate,
) -> MasterShift:
    master = db.get(Master, data.master_id)
    if master is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Master not found: {data.master_id}",
        )

    validate_shift_payload(data)
    assert_no_shift_conflicts(db, data)

    shift_code = generate_shift_code(master, data)
    existing_shift_code = db.scalar(
        select(MasterShift.id).where(MasterShift.shift_code == shift_code)
    )
    if existing_shift_code is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Shift code already exists: {shift_code}",
        )

    shift = MasterShift(
        shift_code=shift_code,
        master_id=data.master_id,
        date=data.date,
        start_time=data.start_time,
        end_time=data.end_time,
        status=data.status,
        note=data.note,
    )
    db.add(shift)
    db.commit()
    db.refresh(shift)

    logger.info(
        "[MASTER_SHIFTS] Shift created: shift_id=%s shift_code=%s master_id=%s date=%s status=%s",
        shift.id,
        shift.shift_code,
        shift.master_id,
        shift.date,
        shift.status,
    )

    return shift


def get_admin_schedule(
    db: Session,
    from_date: date,
    to_date: date,
) -> AdminScheduleResponse:
    _validate_date_range(from_date, to_date, max_days=31)

    days = _date_range(from_date, to_date)
    masters = list(
        db.scalars(
            select(Master).order_by(Master.sort_order, Master.id)
        ).all()
    )
    shifts = list(
        db.scalars(
            select(MasterShift)
            .where(
                MasterShift.date >= from_date,
                MasterShift.date <= to_date,
            )
            .order_by(MasterShift.date, MasterShift.id)
        ).all()
    )
    shifts_by_master_date = {
        (shift.master_id, shift.date): shift
        for shift in shifts
    }

    schedule_masters = [
        AdminScheduleMaster(
            id=master.id,
            name=f"{master.first_name} {master.last_name}",
            is_active=master.is_active,
            days=[
                _shift_to_admin_schedule_day(
                    day,
                    shifts_by_master_date.get((master.id, day)),
                )
                for day in days
            ],
        )
        for master in masters
    ]

    return AdminScheduleResponse(
        from_date=from_date,
        to_date=to_date,
        days=days,
        masters=schedule_masters,
    )


def upsert_admin_schedule_day(
    db: Session,
    data: AdminScheduleDayUpsert,
) -> AdminScheduleDay:
    master = _get_master_or_404(db, data.master_id)
    start_time, end_time = _validate_admin_schedule_payload(data)

    shift = _get_shift_for_master_date(db, data.master_id, data.date)
    shift_code = _generate_admin_shift_code(
        master=master,
        shift_date=data.date,
        status_value=data.status,
        start_time=start_time,
    )

    if shift is None:
        shift = MasterShift(
            shift_code=shift_code,
            master_id=data.master_id,
            date=data.date,
            status=data.status,
            start_time=start_time,
            end_time=end_time,
            note=data.note,
        )
        db.add(shift)
    else:
        shift.shift_code = shift_code
        shift.status = data.status
        shift.start_time = start_time
        shift.end_time = end_time
        shift.note = data.note

    db.commit()
    db.refresh(shift)

    logger.info(
        "[ADMIN] Schedule day updated: master_id=%s date=%s status=%s",
        data.master_id,
        data.date,
        data.status,
    )

    return _shift_to_admin_schedule_day(data.date, shift)


def upsert_admin_schedule_range(
    db: Session,
    data: AdminScheduleRangeUpsert,
) -> AdminScheduleRangeResponse:
    _validate_date_range(data.from_date, data.to_date, max_days=60)
    master = _get_master_or_404(db, data.master_id)
    start_time, end_time = _validate_admin_schedule_payload(data)
    days = _date_range(data.from_date, data.to_date)
    existing_shifts = {
        shift.date: shift
        for shift in db.scalars(
            select(MasterShift).where(
                MasterShift.master_id == data.master_id,
                MasterShift.date >= data.from_date,
                MasterShift.date <= data.to_date,
            )
        ).all()
    }

    for day in days:
        shift = existing_shifts.get(day)
        shift_code = _generate_admin_shift_code(
            master=master,
            shift_date=day,
            status_value=data.status,
            start_time=start_time,
        )

        if shift is None:
            shift = MasterShift(
                shift_code=shift_code,
                master_id=data.master_id,
                date=day,
                status=data.status,
                start_time=start_time,
                end_time=end_time,
                note=data.note,
            )
            db.add(shift)
            continue

        shift.shift_code = shift_code
        shift.status = data.status
        shift.start_time = start_time
        shift.end_time = end_time
        shift.note = data.note

    db.commit()

    logger.info(
        "[ADMIN] Schedule range updated: master_id=%s from_date=%s to_date=%s status=%s count=%s",
        data.master_id,
        data.from_date,
        data.to_date,
        data.status,
        len(days),
    )

    return AdminScheduleRangeResponse(
        success=True,
        message="Schedule range updated",
        updated_count=len(days),
    )


def generate_shift_code(master: Master, data: MasterShiftCreate) -> str:
    base_code = f"{master.initials}-M{master.id}-{data.date.isoformat()}"

    if data.status == "working":
        return f"{base_code}-{_format_shift_time(data)}"

    if data.status == "extra_day":
        return f"{base_code}-EXTRA-{_format_shift_time(data)}"

    return f"{base_code}-{data.status.upper()}"


def _generate_admin_shift_code(
    master: Master,
    shift_date: date,
    status_value: str,
    start_time: time | None,
) -> str:
    base_code = f"{master.initials}-M{master.id}-{shift_date.isoformat()}"

    if status_value == "working":
        return f"{base_code}-{_format_time_for_code(start_time)}"

    if status_value == "extra_day":
        return f"{base_code}-EXTRA-{_format_time_for_code(start_time)}"

    return f"{base_code}-{status_value.upper()}"


def validate_shift_payload(data: MasterShiftCreate) -> None:
    if data.status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid shift status: {data.status}",
        )

    if data.status in WORKING_STATUSES:
        if data.start_time is None or data.end_time is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_time and end_time are required for working shifts",
            )

        if data.start_time >= data.end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_time must be before end_time",
            )
        return

    if data.start_time is not None or data.end_time is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"start_time and end_time must be null for {data.status} shifts",
        )


def assert_no_shift_conflicts(db: Session, data: MasterShiftCreate) -> None:
    same_day_statement = select(MasterShift).where(
        MasterShift.master_id == data.master_id,
        MasterShift.date == data.date,
    )

    if data.status in WORKING_STATUSES:
        unavailable_shift = db.scalar(
            same_day_statement.where(MasterShift.status.in_(UNAVAILABLE_STATUSES))
        )
        if unavailable_shift is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Cannot create working shift because this master already has "
                    f"{unavailable_shift.status} status on {data.date}"
                ),
            )

        overlapping_shift = db.scalar(
            same_day_statement.where(
                MasterShift.status.in_(WORKING_STATUSES),
                MasterShift.start_time < data.end_time,
                MasterShift.end_time > data.start_time,
            )
        )
        if overlapping_shift is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Shift overlaps existing shift: "
                    f"{overlapping_shift.shift_code}"
                ),
            )
        return

    working_shift = db.scalar(
        same_day_statement.where(MasterShift.status.in_(WORKING_STATUSES))
    )
    if working_shift is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Cannot create unavailable status because this master already has "
                f"working shift {working_shift.shift_code} on {data.date}"
            ),
        )

    unavailable_shift = db.scalar(
        same_day_statement.where(MasterShift.status.in_(UNAVAILABLE_STATUSES))
    )
    if unavailable_shift is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Unavailable status already exists for this master/date: "
                f"{unavailable_shift.shift_code}"
            ),
        )


def _format_shift_time(data: MasterShiftCreate) -> str:
    if data.start_time is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_time is required to generate shift code",
        )

    return data.start_time.strftime("%H%M")


def _format_time_for_code(value: time | None) -> str:
    if value is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_time is required to generate shift code",
        )

    return value.strftime("%H%M")


def _get_master_or_404(db: Session, master_id: int) -> Master:
    master = db.get(Master, master_id)
    if master is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Master not found: {master_id}",
        )

    return master


def _get_shift_for_master_date(
    db: Session,
    master_id: int,
    shift_date: date,
) -> MasterShift | None:
    return db.scalar(
        select(MasterShift).where(
            MasterShift.master_id == master_id,
            MasterShift.date == shift_date,
        )
    )


def _validate_date_range(
    from_date: date,
    to_date: date,
    max_days: int,
) -> None:
    if from_date > to_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="from_date must be before or equal to to_date",
        )

    day_count = (to_date - from_date).days + 1
    if day_count > max_days:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Date range cannot exceed {max_days} days",
        )


def _date_range(from_date: date, to_date: date) -> list[date]:
    return [
        from_date + timedelta(days=offset)
        for offset in range((to_date - from_date).days + 1)
    ]


def _validate_admin_schedule_payload(
    data: AdminScheduleDayUpsert | AdminScheduleRangeUpsert,
) -> tuple[time | None, time | None]:
    if data.status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid shift status: {data.status}",
        )

    if data.status not in WORKING_STATUSES:
        return None, None

    if data.start_time is None or data.end_time is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_time and end_time are required for working shifts",
        )

    start_time = _parse_time(data.start_time, "start_time")
    end_time = _parse_time(data.end_time, "end_time")

    if start_time >= end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_time must be before end_time",
        )

    return start_time, end_time


def _parse_time(value: str, field_name: str) -> time:
    try:
        return datetime.strptime(value, "%H:%M").time()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} must be in HH:MM format",
        ) from exc


def _shift_to_admin_schedule_day(
    value_date: date,
    shift: MasterShift | None,
) -> AdminScheduleDay:
    if shift is None:
        return AdminScheduleDay(
            date=value_date,
            shift_id=None,
            status="not_set",
            start_time=None,
            end_time=None,
            note=None,
        )

    return AdminScheduleDay(
        date=value_date,
        shift_id=shift.id,
        status=shift.status,
        start_time=_format_time(shift.start_time),
        end_time=_format_time(shift.end_time),
        note=shift.note,
    )


def _format_time(value: time | None) -> str | None:
    if value is None:
        return None

    return value.strftime("%H:%M")
