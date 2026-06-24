from sqlalchemy.orm import Session

from app.ai.schemas import BookingIntent, ExtractedBookingIntent
from app.modules.booking_ai.response_messages import format_service_names
from app.modules.booking_ai.schemas import BookingAssistantMaster, BookingIntentResponse
from app.modules.booking_ai.service_matching import (
    match_public_services_by_name,
    normalize_text,
)
from app.modules.masters.models import Master
from app.modules.masters.service import list_public_masters
from app.modules.services.models import Service
from app.modules.services.service import list_public_services


def build_master_info_response(
    db: Session,
    extracted: ExtractedBookingIntent,
) -> BookingIntentResponse:
    masters = list_public_masters(db)
    if extracted.intent == BookingIntent.list_masters:
        return BookingIntentResponse(
            intent=BookingIntent.list_masters,
            master_query=extracted.master_query,
            assistant_message=build_masters_list_message(masters),
            masters=build_assistant_masters(masters),
            actions=[],
        )

    if extracted.intent == BookingIntent.master_service_info:
        return build_master_service_info_response(db, masters, extracted)

    return build_single_master_info_response(masters, extracted)


def build_single_master_info_response(
    masters: list[Master],
    extracted: ExtractedBookingIntent,
) -> BookingIntentResponse:
    master_query = extracted.master_query
    if not master_query:
        return BookingIntentResponse(
            intent=BookingIntent.list_masters,
            master_query=master_query,
            assistant_message=build_masters_list_message(masters),
            masters=build_assistant_masters(masters),
            actions=[],
        )

    matches = match_public_masters_by_name(masters, master_query)
    if len(matches) == 1:
        master = matches[0]
        return BookingIntentResponse(
            intent=BookingIntent.master_info,
            master_query=master_full_name(master),
            assistant_message=build_single_master_message(master),
            masters=build_assistant_masters([master]),
            actions=[],
        )

    if len(matches) > 1:
        return BookingIntentResponse(
            intent=BookingIntent.master_info,
            master_query=master_query,
            assistant_message=(
                f"I found a few matching masters: {format_master_names(matches)}. "
                "Which one do you mean?"
            ),
            masters=build_assistant_masters(matches),
            actions=[],
        )

    return BookingIntentResponse(
        intent=BookingIntent.master_info,
        master_query=master_query,
        assistant_message=f"I couldn't find that master. Available masters are: {format_master_names(masters)}.",
        masters=build_assistant_masters(masters),
        actions=[],
    )


def build_master_service_info_response(
    db: Session,
    masters: list[Master],
    extracted: ExtractedBookingIntent,
) -> BookingIntentResponse:
    service_result = resolve_public_service_for_master_info(db, extracted.service_query)
    if isinstance(service_result, BookingIntentResponse):
        return service_result

    service = service_result
    compatible_masters = list_public_masters(db, service_id=service.id)
    master_query = extracted.master_query

    if not master_query:
        return BookingIntentResponse(
            intent=BookingIntent.master_service_info,
            service_query=service.name,
            master_query=master_query,
            assistant_message=build_service_masters_message(service, compatible_masters),
            masters=build_assistant_masters(compatible_masters),
            actions=[],
        )

    master_matches = match_public_masters_by_name(masters, master_query)
    if len(master_matches) == 1:
        master = master_matches[0]
        if master_can_perform_service(master, service):
            assistant_message = (
                f"Yes, {master_full_name(master)} can perform {service.name}. "
                "You can continue with the booking form to choose a date and time."
            )
        else:
            available_names = format_master_names(compatible_masters)
            assistant_message = (
                f"I couldn't confirm that {master_full_name(master)} performs {service.name}. "
                f"Available masters for {service.name} are: {available_names}."
            )

        return BookingIntentResponse(
            intent=BookingIntent.master_service_info,
            service_query=service.name,
            master_query=master_full_name(master),
            assistant_message=assistant_message,
            masters=build_assistant_masters([master]),
            actions=[],
        )

    if len(master_matches) > 1:
        return BookingIntentResponse(
            intent=BookingIntent.master_service_info,
            service_query=service.name,
            master_query=master_query,
            assistant_message=(
                f"I found a few matching masters: {format_master_names(master_matches)}. "
                "Which one do you mean?"
            ),
            masters=build_assistant_masters(master_matches),
            actions=[],
        )

    return BookingIntentResponse(
        intent=BookingIntent.master_service_info,
        service_query=service.name,
        master_query=master_query,
        assistant_message=f"I couldn't find that master. Available masters are: {format_master_names(masters)}.",
        masters=build_assistant_masters(masters),
        actions=[],
    )


def resolve_public_service_for_master_info(
    db: Session,
    service_query: str | None,
) -> Service | BookingIntentResponse:
    services = list_public_services(db)
    if not service_query:
        return BookingIntentResponse(
            intent=BookingIntent.master_service_info,
            assistant_message=f"Which service do you mean? Available services are: {format_service_names(services)}.",
            actions=[],
        )

    matches = match_public_services_by_name(services, service_query)
    if len(matches) == 1:
        return matches[0]

    if len(matches) > 1:
        return BookingIntentResponse(
            intent=BookingIntent.master_service_info,
            service_query=service_query,
            assistant_message=(
                f"I found a few matching services: {format_service_names(matches)}. "
                "Which one do you mean?"
            ),
            actions=[],
        )

    return BookingIntentResponse(
        intent=BookingIntent.master_service_info,
        service_query=service_query,
        assistant_message=f"I couldn't find that service. Available services are: {format_service_names(services)}.",
        actions=[],
    )


def match_public_masters_by_name(
    masters: list[Master],
    master_query: str,
) -> list[Master]:
    normalized_query = normalize_text(master_query)
    if not normalized_query:
        return []

    exact_matches = [
        master
        for master in masters
        if normalize_text(master_full_name(master)) == normalized_query
    ]
    if exact_matches:
        return exact_matches

    return [
        master
        for master in masters
        if normalized_query in normalize_text(master_full_name(master))
    ]


def master_can_perform_service(master: Master, service: Service) -> bool:
    return any(
        linked_service.id == service.id and linked_service.is_active
        for linked_service in master.services
    )


def build_masters_list_message(masters: list[Master]) -> str:
    if not masters:
        return "There are no public masters available right now."

    masters_text = "; ".join(
        f"{master_full_name(master)} - {master.role}"
        for master in masters
    )
    return f"Our masters are: {masters_text}."


def build_single_master_message(master: Master) -> str:
    message = (
        f"{master_full_name(master)} is a {master.role}. "
        "This master is available as one of our public masters."
    )
    bio = (master.bio or "").strip()
    if bio:
        message = f"{master_full_name(master)} is a {master.role}. Bio: {bio}"
    return f"{message} You can choose this master during booking."


def build_service_masters_message(service: Service, masters: list[Master]) -> str:
    if not masters:
        return (
            f"I couldn't confirm any public masters for {service.name}. "
            "You can choose an available master during booking."
        )

    return f"{service.name} can be performed by: {format_master_names(masters)}."


def build_assistant_masters(masters: list[Master]) -> list[BookingAssistantMaster]:
    return [
        BookingAssistantMaster(
            id=master.id,
            name=master_full_name(master),
            role=master.role,
            bio=master.bio or "",
        )
        for master in masters
    ]


def format_master_names(masters: list[Master]) -> str:
    return ", ".join(master_full_name(master) for master in masters) or "none"


def master_full_name(master: Master) -> str:
    return f"{master.first_name} {master.last_name}".strip()
