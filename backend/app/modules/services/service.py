from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.services.models import Service
from app.modules.services.schemas import ServiceCreate


def create_service(db: Session, data: ServiceCreate) -> Service:
    service = Service(**data.model_dump())
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


def list_public_services(db: Session) -> list[Service]:
    statement = (
        select(Service)
        .where(Service.is_active.is_(True))
        .order_by(Service.sort_order, Service.id)
    )
    return list(db.scalars(statement).all())


def list_admin_services(db: Session) -> list[Service]:
    statement = select(Service).order_by(Service.sort_order, Service.id)
    return list(db.scalars(statement).all())
