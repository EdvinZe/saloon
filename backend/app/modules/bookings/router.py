import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.bookings.schemas import (
    BookingAvailabilityCheckResponse,
    BookingCancelRequest,
    BookingCancelResponse,
    BookingCreate,
    BookingDepositIntentResponse,
    BookingPaymentResultResponse,
    BookingPublic,
)
from app.modules.bookings.service import (
    cancel_booking_by_manage_token,
    check_booking_availability,
    create_confirmed_booking,
    get_booking_by_manage_token,
    get_booking_by_payment_intent,
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


@router.get(
    "/payment-result",
    response_model=BookingPaymentResultResponse,
)
def get_booking_payment_result_endpoint(
    payment_intent: str = "",
    db: Session = Depends(get_db),
):
    if not payment_intent or not payment_intent.strip():
        return BookingPaymentResultResponse(
            status="not_found",
            message="Payment intent is missing",
            booking=None,
        )

    booking = get_booking_by_payment_intent(db, payment_intent)
    if booking is not None:
        return BookingPaymentResultResponse(
            status="confirmed",
            message="Booking confirmed",
            booking=booking,
        )

    return BookingPaymentResultResponse(
        status="processing",
        message="Payment received. Booking is still being confirmed.",
        booking=None,
    )


@router.get(
    "/manage",
    response_model=BookingPublic,
)
def get_booking_manage_endpoint(
    token: str = "",
    db: Session = Depends(get_db),
):
    if not token or not token.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking token is required",
        )

    booking = get_booking_by_manage_token(db, token)
    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    return booking


@router.post(
    "/manage/cancel",
    response_model=BookingCancelResponse,
)
def cancel_booking_manage_endpoint(
    data: BookingCancelRequest,
    db: Session = Depends(get_db),
):
    booking = cancel_booking_by_manage_token(db, data.token)
    return BookingCancelResponse(
        success=True,
        message="Booking cancelled",
        booking=booking,
    )


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
