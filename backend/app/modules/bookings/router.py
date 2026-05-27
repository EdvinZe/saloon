import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.bookings.schemas import (
    BookingAvailabilityCheckResponse,
    BookingCreate,
    BookingDepositIntentResponse,
    BookingPublic,
)
from app.modules.bookings.service import (
    check_booking_availability,
    create_confirmed_booking,
    validate_booking_creation,
)
from app.modules.payments.stripe_service import create_booking_deposit_payment_intent

logger = logging.getLogger(__name__)

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
    "/deposit-intent",
    response_model=BookingDepositIntentResponse,
)
def create_booking_deposit_intent_endpoint(
    data: BookingCreate,
    db: Session = Depends(get_db),
):
    logger.info(
        "[BOOKINGS] Deposit intent requested: service_id=%s master_id=%s "
        "date=%s time=%s",
        data.service_id,
        data.master_id,
        data.date,
        data.time,
    )
    validate_booking_creation(db, data)
    return create_booking_deposit_payment_intent(data)


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
