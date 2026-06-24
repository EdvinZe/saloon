from decimal import Decimal

from app.ai.schemas import BookingIntent, CurrentBookingDraft
from app.modules.booking_ai.draft import (
    format_booking_details,
    has_booking_details,
    has_complete_booking_details,
)
from app.modules.booking_ai.service_matching import normalize_text
from app.modules.booking_ai.schemas import BookingAssistantService
from app.modules.services.models import Service
from app.modules.services.service import get_service_total_duration_minutes


def build_assistant_message(
    *,
    booking_draft: CurrentBookingDraft,
    intent: BookingIntent,
    missing_fields: list[str],
    user_message: str,
    availability_result=None,
) -> str:
    if availability_result is not None:
        if availability_result.error_message:
            return availability_result.error_message
        if availability_result.requested_time_available:
            option_names = ", ".join(
                option.master_name for option in availability_result.available_options
            )
            label = "Available master" if len(availability_result.available_options) == 1 else "Available masters"
            return (
                f"Good news - {booking_draft.service_query} is available on {booking_draft.date} "
                f"at {booking_draft.time}. {label}: {option_names}. "
                "You can continue with the booking form to confirm it."
            )
        if availability_result.nearest_options:
            options_text = " or ".join(
                f"{option.time} with {option.master_name}"
                for option in availability_result.nearest_options
            )
            return (
                f"{booking_draft.time} is not available for {booking_draft.service_query} "
                f"on {booking_draft.date}. The closest available options are {options_text}. "
                "You can continue with the booking form to choose one."
            )
        return (
            f"{booking_draft.time} is not available for {booking_draft.service_query} "
            f"on {booking_draft.date}, and I could not find same-day alternatives. "
            "You can continue with the booking form to choose another time."
        )

    lowered_message = user_message.lower()
    asks_availability = intent == BookingIntent.check_available_masters or any(
        phrase in lowered_message
        for phrase in ("available", "availability", "free", "master can", "what master")
    )

    if intent == BookingIntent.unsupported:
        return "I can help with booking questions, but I cannot access private booking, payment, or admin data."
    if intent == BookingIntent.greeting and not has_booking_details(booking_draft):
        return "Hi! I can help prepare your booking details. What service would you like?"

    if "service" in missing_fields:
        return "What service are you looking for?"
    if "date" in missing_fields:
        return "What date would you like to book?"
    if "time" in missing_fields:
        return "What time would you like to book?"

    if has_complete_booking_details(booking_draft):
        if asks_availability:
            return (
                "I have the booking details. Live availability is handled by the booking system, "
                "so you can continue with the booking form to see available masters and times."
            )
        return (
            f"I understood that you want {format_booking_details(booking_draft)}. "
            "I can help you check matching booking options."
        )

    if has_booking_details(booking_draft):
        return (
            f"I have {format_booking_details(booking_draft)} so far. "
            "Tell me the missing detail and I can prepare the booking request."
        )

    return "How can I help with your booking?"


def build_assistant_services(services: list[Service]) -> list[BookingAssistantService]:
    return [
        BookingAssistantService(
            id=service.id,
            name=service.name,
            description=service.description or "",
            duration_minutes=get_service_total_duration_minutes(service),
            price=format_service_price(service.price),
        )
        for service in services
    ]


def build_services_list_message(services: list[Service]) -> str:
    if not services:
        return "There are no services available to book right now."

    services_text = "; ".join(
        f"{service.name} - {get_service_total_duration_minutes(service)} min - {format_service_price(service.price)}"
        for service in services
    )
    return f"We currently offer: {services_text}."


def build_single_service_message(service: Service) -> str:
    description = (service.description or "").strip()
    message = (
        f"{service.name} costs {format_service_price(service.price)} and takes about "
        f"{get_service_total_duration_minutes(service)} minutes."
    )
    if description and normalize_text(description) != normalize_text(service.name):
        message = f"{message} {description}"
    return message


def format_service_names(services: list[Service]) -> str:
    return ", ".join(service.name for service in services) or "none"


def format_service_price(price: Decimal) -> str:
    normalized = price.quantize(Decimal("0.01"))
    if normalized == normalized.to_integral():
        return f"€{normalized:.0f}"
    return f"€{normalized:.2f}"
