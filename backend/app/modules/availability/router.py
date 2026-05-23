from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.availability.schemas import AvailableSlotStatus
from app.modules.availability.service import (
    list_available_masters,
    list_available_slots,
)
from app.modules.masters.schemas import MasterPublic

router = APIRouter()


@router.get("/slots", response_model=list[AvailableSlotStatus])
def get_available_slots(
    service_id: int,
    date: date,
    db: Session = Depends(get_db),
):
    return list_available_slots(
        db=db,
        service_id=service_id,
        selected_date=date,
    )


@router.get("/masters", response_model=list[MasterPublic])
def get_available_masters(
    service_id: int,
    date: date,
    time: str,
    db: Session = Depends(get_db),
):
    return list_available_masters(
        db=db,
        service_id=service_id,
        selected_date=date,
        selected_time=time,
    )
