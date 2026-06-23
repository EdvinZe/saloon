from app.ai.schemas import ExtractedBookingIntent


def test_extracted_booking_intent_normalizes_pm_time():
    result = ExtractedBookingIntent(
        intent="find_booking_slot",
        service_query="Haircut",
        date="2026-06-24",
        time_preference="at 3pm",
        missing_fields=[],
        assistant_message="I can help find options at 3pm.",
    )

    assert result.time_preference_type == "at"
    assert result.time == "15:00"
    assert result.time_preference == "at 15:00"


def test_extracted_booking_intent_normalizes_24_hour_time():
    result = ExtractedBookingIntent(
        intent="find_booking_slot",
        service_query="Haircut",
        date="2026-06-24",
        time_preference="after 15",
        missing_fields=[],
        assistant_message="I can help find options after 15:00.",
    )

    assert result.time_preference_type == "after"
    assert result.time == "15:00"
    assert result.time_preference == "after 15:00"


def test_extracted_booking_intent_normalizes_dot_time():
    result = ExtractedBookingIntent(
        intent="find_booking_slot",
        service_query="Haircut",
        date="2026-06-24",
        time_preference="at 15.00",
        missing_fields=[],
        assistant_message="I can help find options at 15.00.",
    )

    assert result.time_preference_type == "at"
    assert result.time == "15:00"
    assert result.time_preference == "at 15:00"


def test_extracted_booking_intent_keeps_broad_time_preference():
    result = ExtractedBookingIntent(
        intent="find_booking_slot",
        service_query="Haircut",
        date="2026-06-24",
        time_preference="morning",
        missing_fields=[],
        assistant_message="I can help find morning options.",
    )

    assert result.time_preference_type == "morning"
    assert result.time is None
    assert result.time_preference == "morning"


def test_extracted_booking_intent_normalizes_empty_strings_to_none():
    result = ExtractedBookingIntent(
        intent="greeting",
        service_query="",
        date="",
        time_preference="",
        time_preference_type="",
        time="",
        master_preference="",
        missing_fields=[""],
        assistant_message="Hello!",
    )

    assert result.service_query is None
    assert result.date is None
    assert result.time_preference is None
    assert result.time_preference_type is None
    assert result.time is None
    assert result.master_preference is None
    assert result.missing_fields == []
