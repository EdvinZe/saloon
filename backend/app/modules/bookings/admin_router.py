from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.bookings.schemas import AdminBookingActionResponse, AdminBookingRead
from app.modules.bookings.service import (
    cancel_admin_booking,
    get_admin_booking,
    list_admin_bookings,
    mark_admin_booking_completed,
    mark_admin_booking_no_show,
)

router = APIRouter()


@router.get("", response_model=list[AdminBookingRead])
def get_admin_bookings(
    date: date | None = None,
    status: str | None = None,
    master_id: int | None = None,
    service_id: int | None = None,
    db: Session = Depends(get_db),
):
    return list_admin_bookings(
        db=db,
        date=date,
        status=status,
        master_id=master_id,
        service_id=service_id,
    )


@router.get("/{booking_id}", response_model=AdminBookingRead)
def get_admin_booking_route(booking_id: int, db: Session = Depends(get_db)):
    return get_admin_booking(db, booking_id)


@router.post("/{booking_id}/complete", response_model=AdminBookingActionResponse)
def complete_admin_booking_route(booking_id: int, db: Session = Depends(get_db)):
    return mark_admin_booking_completed(db, booking_id)


@router.post("/{booking_id}/no-show", response_model=AdminBookingActionResponse)
def no_show_admin_booking_route(booking_id: int, db: Session = Depends(get_db)):
    return mark_admin_booking_no_show(db, booking_id)


@router.post("/{booking_id}/cancel", response_model=AdminBookingActionResponse)
def cancel_admin_booking_route(booking_id: int, db: Session = Depends(get_db)):
    return cancel_admin_booking(db, booking_id)
