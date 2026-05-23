import logging
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.master_shifts.models import MasterShift
from app.modules.master_shifts.schemas import MasterShiftCreate
from app.modules.masters.models import Master

logger = logging.getLogger(__name__)

WORKING_STATUSES = {"working", "extra_day"}
UNAVAILABLE_STATUSES = {"sick", "vacation", "other"}
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


def generate_shift_code(master: Master, data: MasterShiftCreate) -> str:
    base_code = f"{master.initials}-M{master.id}-{data.date.isoformat()}"

    if data.status == "working":
        return f"{base_code}-{_format_shift_time(data)}"

    if data.status == "extra_day":
        return f"{base_code}-EXTRA-{_format_shift_time(data)}"

    return f"{base_code}-{data.status.upper()}"


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
