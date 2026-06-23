from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from app.ai.schemas import (
    BookingConversationMessage,
    BookingIntent,
    BookingIntentTimePreferenceType,
    CurrentBookingDraft,
)


MAX_BOOKING_AI_MESSAGE_LENGTH = 1000
MAX_BOOKING_AI_CONTEXT_MESSAGES = 10


class BookingIntentRequest(BaseModel):
    message: Annotated[str, Field(min_length=1, max_length=MAX_BOOKING_AI_MESSAGE_LENGTH)]
    messages: list[BookingConversationMessage] = Field(default_factory=list)
    current_booking_draft: CurrentBookingDraft | None = None

    @field_validator("message", mode="before")
    @classmethod
    def trim_message(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("messages", mode="after")
    @classmethod
    def limit_messages(
        cls,
        value: list[BookingConversationMessage],
    ) -> list[BookingConversationMessage]:
        return value[-MAX_BOOKING_AI_CONTEXT_MESSAGES:]


class BookingIntentResponse(BaseModel):
    intent: BookingIntent
    service_query: str | None = None
    date: str | None = None
    time_preference: str | None = None
    time_preference_type: BookingIntentTimePreferenceType | None = None
    time: str | None = None
    master_preference: str | None = None
    missing_fields: list[str] = Field(default_factory=list)
    assistant_message: str
