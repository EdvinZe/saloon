from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from app.ai.schemas import BookingIntent


MAX_BOOKING_AI_MESSAGE_LENGTH = 1000


class BookingIntentRequest(BaseModel):
    message: Annotated[str, Field(min_length=1, max_length=MAX_BOOKING_AI_MESSAGE_LENGTH)]

    @field_validator("message", mode="before")
    @classmethod
    def trim_message(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value


class BookingIntentResponse(BaseModel):
    intent: BookingIntent
    service_query: str | None = None
    date: str | None = None
    time_preference: str | None = None
    master_preference: str | None = None
    missing_fields: list[str] = Field(default_factory=list)
    assistant_message: str
