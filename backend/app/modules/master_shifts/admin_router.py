from datetime import date

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.master_shifts.schemas import MasterShiftAdmin, MasterShiftCreate
from app.modules.master_shifts.service import (
    create_master_shift,
    list_master_shifts,
)

router = APIRouter()


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
