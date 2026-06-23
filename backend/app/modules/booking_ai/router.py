from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.booking_ai.schemas import BookingIntentRequest, BookingIntentResponse
from app.modules.booking_ai.service import extract_booking_intent

router = APIRouter()


@router.post("/booking-intent", response_model=BookingIntentResponse)
def create_booking_intent(
    data: BookingIntentRequest,
    db: Session = Depends(get_db),
) -> BookingIntentResponse:
    return extract_booking_intent(
        db,
        data.message,
        data.messages,
        data.current_booking_draft,
    )
