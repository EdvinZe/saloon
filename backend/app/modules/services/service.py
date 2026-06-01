import logging
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.services.models import Service
from app.modules.services.schemas import AdminServiceCreate, AdminServiceUpdate, ServiceCreate

logger = logging.getLogger(__name__)


def get_service_total_duration_minutes(service: Service) -> int:
    total_duration = getattr(service, "total_duration_minutes", None)
    if isinstance(total_duration, int):
        return total_duration

    return service.duration_minutes + (service.cleanup_time_minutes or 0)


def create_service(db: Session, data: ServiceCreate) -> Service:
    service = Service(**data.model_dump())
    db.add(service)
    db.commit()
    db.refresh(service)
    logger.info(
        "[SERVICES] Service created: service_id=%s name=%s",
        service.id,
        service.name,
    )
    return service


def list_public_services(db: Session) -> list[Service]:
    logger.debug("[SERVICES] Public services requested")
    statement = (
        select(Service)
        .where(Service.is_active.is_(True))
        .order_by(Service.sort_order, Service.id)
    )
    return list(db.scalars(statement).all())


def list_admin_services(db: Session) -> list[Service]:
    statement = select(Service).order_by(Service.sort_order, Service.name, Service.id)
    return list(db.scalars(statement).all())


def get_admin_service(db: Session, service_id: int) -> Service:
    service = db.get(Service, service_id)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service not found: {service_id}",
        )

    return service


def create_admin_service(db: Session, data: AdminServiceCreate) -> Service:
    payload = _admin_service_create_payload(data)
    service = Service(**payload)
    db.add(service)
    db.commit()
    db.refresh(service)

    logger.info(
        "[ADMIN] Service created: service_id=%s name=%s",
        service.id,
        service.name,
    )

    return service


def update_admin_service(
    db: Session,
    service_id: int,
    data: AdminServiceUpdate,
) -> Service:
    service = get_admin_service(db, service_id)
    payload = _admin_service_update_payload(data)

    for field_name, value in payload.items():
        setattr(service, field_name, value)

    db.commit()
    db.refresh(service)

    logger.info("[ADMIN] Service updated: service_id=%s", service.id)

    return service


def activate_admin_service(db: Session, service_id: int) -> Service:
    service = get_admin_service(db, service_id)
    service.is_active = True
    db.commit()
    db.refresh(service)

    logger.info("[ADMIN] Service activated: service_id=%s", service.id)

    return service


def deactivate_admin_service(db: Session, service_id: int) -> Service:
    service = get_admin_service(db, service_id)
    service.is_active = False
    db.commit()
    db.refresh(service)

    logger.info("[ADMIN] Service deactivated: service_id=%s", service.id)

    return service


def _admin_service_create_payload(data: AdminServiceCreate) -> dict[str, object]:
    payload = data.model_dump()
    price_cents = payload.pop("price_cents")
    payload["price"] = _price_from_cents(price_cents)
    return payload


def _admin_service_update_payload(data: AdminServiceUpdate) -> dict[str, object]:
    payload = data.model_dump(exclude_unset=True)

    if "price_cents" in payload:
        price_cents = payload.pop("price_cents")
        if price_cents is not None:
            payload["price"] = _price_from_cents(price_cents)

    return payload


def _price_from_cents(price_cents: int) -> Decimal:
    return Decimal(price_cents) / Decimal("100")
