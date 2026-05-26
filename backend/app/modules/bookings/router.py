from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.bookings.schemas import (
    BookingAvailabilityCheckResponse,
    BookingCreate,
    BookingPublic,
)
from app.modules.bookings.service import (
    check_booking_availability,
    create_confirmed_booking,
)

router = APIRouter()


@router.post(
    "/check-availability",
    response_model=BookingAvailabilityCheckResponse,
)
def check_booking_availability_endpoint(
    data: BookingCreate,
    db: Session = Depends(get_db),
):
    return check_booking_availability(db, data)


@router.post(
    "/confirmed",
    response_model=BookingPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_confirmed_booking_endpoint(
    data: BookingCreate,
    db: Session = Depends(get_db),
):
    # Development/simple flow. Stripe checkout endpoint will be added later.
    return create_confirmed_booking(db, data, source="online")
