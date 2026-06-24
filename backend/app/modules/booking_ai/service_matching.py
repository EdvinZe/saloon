import re

from sqlalchemy.orm import Session

from app.modules.services.models import Service
from app.modules.services.service import list_public_services


def resolve_service_query(db: Session, service_query: str | None) -> Service | None:
    if not service_query:
        return None

    normalized_query = normalize_text(service_query)
    services = list_public_services(db)

    for service in services:
        if normalize_text(service.name) == normalized_query:
            return service

    for service in services:
        service_name = normalize_text(service.name)
        if normalized_query in service_name or service_name in normalized_query:
            return service

    for service in services:
        service_description = normalize_text(service.description or "")
        if service_description and (
            normalized_query in service_description or service_description in normalized_query
        ):
            return service

    return None


def match_public_services_by_name(
    services: list[Service],
    service_query: str,
) -> list[Service]:
    normalized_query = normalize_service_match_text(service_query)
    if not normalized_query:
        return []

    exact_matches = [
        service
        for service in services
        if normalize_service_match_text(service.name) == normalized_query
    ]
    if exact_matches:
        return exact_matches

    return [
        service
        for service in services
        if is_service_name_match(normalized_query, normalize_service_match_text(service.name))
    ]


def is_service_name_match(normalized_query: str, normalized_name: str) -> bool:
    return normalized_query in normalized_name


def normalize_service_match_text(value: str) -> str:
    words = normalize_text(value).split()
    stop_words = {"and"}
    return " ".join(word for word in words if word not in stop_words)


def normalize_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()
