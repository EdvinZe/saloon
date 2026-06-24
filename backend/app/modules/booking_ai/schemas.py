from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator

from app.ai.schemas import (
    BookingConversationMessage,
    BookingIntent,
    BookingIntentTimePreferenceType,
    BookingNextAction,
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
    master_query: str | None = None
    date: str | None = None
    time_preference: str | None = None
    time_preference_type: BookingIntentTimePreferenceType | None = None
    time: str | None = None
    master_preference: str | None = None
    booking_draft: CurrentBookingDraft = Field(default_factory=CurrentBookingDraft)
    missing_fields: list[str] = Field(default_factory=list)
    next_action: BookingNextAction = BookingNextAction.none
    assistant_message: str
    requested_time_available: bool | None = None
    available_options: list["BookingAvailabilityOption"] = Field(default_factory=list)
    nearest_options: list["BookingNearestAvailabilityOption"] = Field(default_factory=list)
    services: list["BookingAssistantService"] = Field(default_factory=list)
    masters: list["BookingAssistantMaster"] = Field(default_factory=list)
    actions: list["BookingAssistantAction"] = Field(default_factory=list)


class BookingAssistantService(BaseModel):
    id: int
    name: str
    description: str = ""
    duration_minutes: int
    price: str


class BookingAssistantMaster(BaseModel):
    id: int
    name: str
    role: str
    bio: str = ""


class BookingAvailabilityOption(BaseModel):
    service_id: int
    service_name: str
    master_id: int
    master_name: str
    date: str
    time: str


class BookingNearestAvailabilityOption(BookingAvailabilityOption):
    direction: str


class BookingAssistantActionPayload(BaseModel):
    service_id: int
    master_id: int
    date: str
    time: str


class BookingAssistantAction(BaseModel):
    type: Literal["prefill_booking"] = "prefill_booking"
    label: str
    payload: BookingAssistantActionPayload
