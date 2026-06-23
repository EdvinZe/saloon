from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class BookingIntent(str, Enum):
    find_booking_slot = "find_booking_slot"
    ask_booking_question = "ask_booking_question"
    unknown = "unknown"


class BookingIntentExtractionContext(BaseModel):
    today: date
    service_names: list[str] = Field(default_factory=list)
    user_message: str


class ExtractedBookingIntent(BaseModel):
    intent: BookingIntent
    service_query: str | None = None
    date: str | None = None
    time_preference: str | None = None
    master_preference: str | None = None
    missing_fields: list[str] = Field(default_factory=list)
    assistant_message: str
