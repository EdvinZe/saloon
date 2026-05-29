import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.services.models import Service
from app.modules.services.schemas import ServiceCreate

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
    statement = select(Service).order_by(Service.sort_order, Service.id)
    return list(db.scalars(statement).all())
