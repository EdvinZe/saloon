from datetime import date
from enum import Enum
import re

from pydantic import BaseModel, Field, field_validator, model_validator


class BookingIntent(str, Enum):
    find_booking_slot = "find_booking_slot"
    ask_booking_question = "ask_booking_question"
    check_available_masters = "check_available_masters"
    flexible_availability_search = "flexible_availability_search"
    service_info = "service_info"
    list_services = "list_services"
    master_info = "master_info"
    list_masters = "list_masters"
    master_service_info = "master_service_info"
    greeting = "greeting"
    unsupported = "unsupported"
    unknown = "unknown"


class BookingIntentTimePreferenceType(str, Enum):
    at = "at"
    exact = "exact"
    after = "after"
    before = "before"
    between = "between"
    any = "any"
    morning = "morning"
    afternoon = "afternoon"
    evening = "evening"
    unknown = "unknown"


class BookingNextAction(str, Enum):
    none = "none"
    ask_service = "ask_service"
    ask_date = "ask_date"
    ask_time = "ask_time"
    ready_to_check_availability = "ready_to_check_availability"
    availability_found = "availability_found"
    availability_alternatives = "availability_alternatives"
    availability_options_found = "availability_options_found"
    unsupported = "unsupported"
    ai_unavailable = "ai_unavailable"


class BookingConversationRole(str, Enum):
    user = "user"
    assistant = "assistant"


class BookingConversationMessage(BaseModel):
    role: BookingConversationRole
    content: str = Field(min_length=1, max_length=1000)

    @field_validator("content", mode="before")
    @classmethod
    def trim_content(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value


class BookingDraftAvailabilityOption(BaseModel):
    service_id: int
    service_name: str
    master_id: int
    master_name: str
    date: str
    time: str


class CurrentBookingDraft(BaseModel):
    service_query: str | None = None
    service_id: int | None = None
    master_query: str | None = None
    date: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    date_range_type: str | None = None
    weekdays: list[str] | None = None
    time: str | None = None
    end_time: str | None = None
    time_preference: str | None = None
    time_preference_type: BookingIntentTimePreferenceType | None = None
    daypart: str | None = None
    limit: int | None = None
    master_preference: str | None = None
    master_id: int | None = None
    master_name: str | None = None
    last_intent: str | None = None
    last_available_options: list[BookingDraftAvailabilityOption] = Field(default_factory=list)
    shown_option_count: int = 0
    excluded_master_ids: list[int] = Field(default_factory=list)

    @field_validator(
        "service_query",
        "master_query",
        "date",
        "start_date",
        "end_date",
        "date_range_type",
        "time",
        "end_time",
        "time_preference",
        "time_preference_type",
        "daypart",
        "master_preference",
        "master_name",
        "last_intent",
        mode="before",
    )
    @classmethod
    def trim_optional_text(cls, value: object) -> object:
        if isinstance(value, str):
            trimmed = value.strip()
            return trimmed or None
        return value


class BookingIntentExtractionContext(BaseModel):
    today: date
    service_names: list[str] = Field(default_factory=list)
    master_names: list[str] = Field(default_factory=list)
    user_message: str
    conversation_messages: list[BookingConversationMessage] = Field(default_factory=list)
    current_booking_draft: CurrentBookingDraft | None = None


class ExtractedBookingIntent(BaseModel):
    intent: BookingIntent
    service_query: str | None = None
    master_query: str | None = None
    date: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    date_range_type: str | None = None
    weekdays: list[str] = Field(default_factory=list)
    time_preference: str | None = None
    time_preference_type: BookingIntentTimePreferenceType | None = None
    time: str | None = None
    end_time: str | None = None
    daypart: str | None = None
    limit: int | None = None
    master_preference: str | None = None
    missing_fields: list[str] = Field(default_factory=list)
    assistant_message: str

    @field_validator(
        "service_query",
        "master_query",
        "date",
        "start_date",
        "end_date",
        "date_range_type",
        "time_preference",
        "time_preference_type",
        "time",
        "end_time",
        "daypart",
        "master_preference",
        mode="before",
    )
    @classmethod
    def empty_string_to_none(cls, value: object) -> object:
        if isinstance(value, str):
            trimmed = value.strip()
            return trimmed or None
        return value

    @field_validator("missing_fields", mode="before")
    @classmethod
    def normalize_missing_fields(cls, value: object) -> object:
        if not isinstance(value, list):
            return []
        return [item for item in value if isinstance(item, str) and item.strip()]

    @field_validator("weekdays", mode="before")
    @classmethod
    def normalize_weekdays(cls, value: object) -> object:
        if not isinstance(value, list):
            return []
        return [
            item.strip().lower()
            for item in value
            if isinstance(item, str) and item.strip()
        ]

    @field_validator("assistant_message", mode="before")
    @classmethod
    def trim_assistant_message(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @model_validator(mode="after")
    def normalize_time_fields(self) -> "ExtractedBookingIntent":
        normalized = _normalize_time(self.time, self.time_preference)
        if normalized is None:
            if self.time_preference:
                preference = self.time_preference.lower()
                for value in ("morning", "afternoon", "evening"):
                    if value in preference:
                        self.time_preference_type = BookingIntentTimePreferenceType(value)
                        self.time = None
                        self.time_preference = value
                        break
            return self

        preference_type, time_value = normalized
        if self.time_preference_type in {
            BookingIntentTimePreferenceType.after,
            BookingIntentTimePreferenceType.before,
            BookingIntentTimePreferenceType.between,
            BookingIntentTimePreferenceType.exact,
        }:
            preference_type = self.time_preference_type
        self.time_preference_type = preference_type
        self.time = time_value
        self.time_preference = f"{preference_type.value} {time_value}"
        self.assistant_message = _build_stable_assistant_message(self)
        return self


def _normalize_time(
    time_value: str | None,
    time_preference: str | None,
) -> tuple[BookingIntentTimePreferenceType, str] | None:
    source = " ".join(value for value in [time_preference, time_value] if value)
    if not source:
        return None

    lowered = source.lower()
    preference_type = BookingIntentTimePreferenceType.at
    if re.search(r"\bafter\b", lowered):
        preference_type = BookingIntentTimePreferenceType.after
    elif re.search(r"\bbefore\b", lowered):
        preference_type = BookingIntentTimePreferenceType.before
    elif re.search(r"\bat\b", lowered):
        preference_type = BookingIntentTimePreferenceType.at

    match = re.search(r"\b([01]?\d|2[0-3])(?:[:.]([0-5]\d))?\s*(am|pm)?\b", lowered)
    if not match:
        return None

    hour = int(match.group(1))
    minute = int(match.group(2) or "0")
    meridiem = match.group(3)

    if meridiem == "pm" and hour < 12:
        hour += 12
    elif meridiem == "am" and hour == 12:
        hour = 0

    return preference_type, f"{hour:02d}:{minute:02d}"


def _build_stable_assistant_message(intent: ExtractedBookingIntent) -> str:
    if intent.intent != BookingIntent.find_booking_slot:
        return intent.assistant_message

    if "service" in intent.missing_fields:
        return "What service would you like to book?"
    if "date" in intent.missing_fields:
        return "What date would you like to book?"
    if "time" in intent.missing_fields:
        return "What time would you prefer?"

    details = []
    if intent.service_query:
        details.append(intent.service_query)
    if intent.date:
        details.append(f"on {intent.date}")
    if intent.time:
        details.append(f"at {intent.time}")
    elif intent.time_preference:
        details.append(intent.time_preference)

    if not details:
        return intent.assistant_message

    return (
        f"I understood that you want {' '.join(details)}. "
        "I can help you check matching booking options."
    )
