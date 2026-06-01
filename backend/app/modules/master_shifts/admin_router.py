from datetime import date

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.master_shifts.schemas import (
    AdminScheduleDay,
    AdminScheduleDayUpsert,
    AdminScheduleRangeResponse,
    AdminScheduleRangeUpsert,
    AdminScheduleResponse,
    MasterShiftAdmin,
    MasterShiftCreate,
)
from app.modules.master_shifts.service import (
    create_master_shift,
    get_admin_schedule,
    list_master_shifts,
    upsert_admin_schedule_day,
    upsert_admin_schedule_range,
)

router = APIRouter()
schedule_router = APIRouter()


@router.get("/", response_model=list[MasterShiftAdmin])
def get_admin_master_shifts(
    master_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    status: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    return list_master_shifts(
        db=db,
        master_id=master_id,
        start_date=start_date,
        end_date=end_date,
        status=status,
        search=search,
    )


@router.post(
    "/",
    response_model=MasterShiftAdmin,
    status_code=status.HTTP_201_CREATED,
)
def create_admin_master_shift(
    data: MasterShiftCreate,
    db: Session = Depends(get_db),
):
    return create_master_shift(db, data)


@schedule_router.get("/", response_model=AdminScheduleResponse)
def get_admin_schedule_route(
    from_date: date,
    to_date: date,
    db: Session = Depends(get_db),
):
    return get_admin_schedule(db, from_date, to_date)


@schedule_router.post("/day", response_model=AdminScheduleDay)
def update_admin_schedule_day(
    data: AdminScheduleDayUpsert,
    db: Session = Depends(get_db),
):
    return upsert_admin_schedule_day(db, data)


@schedule_router.post("/range", response_model=AdminScheduleRangeResponse)
def update_admin_schedule_range(
    data: AdminScheduleRangeUpsert,
    db: Session = Depends(get_db),
):
    return upsert_admin_schedule_range(db, data)
