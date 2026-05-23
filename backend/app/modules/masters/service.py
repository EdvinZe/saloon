import logging

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.masters.models import Master, MasterService
from app.modules.masters.schemas import MasterCreate
from app.modules.services.models import Service

logger = logging.getLogger(__name__)


def list_public_masters(
    db: Session,
    service_id: int | None = None,
) -> list[Master]:
    statement = (
        select(Master)
        .where(Master.is_active.is_(True))
        .options(selectinload(Master.service_links).selectinload(MasterService.service))
        .order_by(Master.sort_order, Master.id)
    )

    if service_id is not None:
        statement = statement.join(MasterService).where(
            MasterService.service_id == service_id
        )

    return list(db.scalars(statement).all())


def list_admin_masters(db: Session) -> list[Master]:
    statement = (
        select(Master)
        .options(selectinload(Master.service_links).selectinload(MasterService.service))
        .order_by(Master.sort_order, Master.id)
    )
    return list(db.scalars(statement).all())


def create_master(db: Session, data: MasterCreate) -> Master:
    service_ids = list(dict.fromkeys(data.service_ids))

    if service_ids:
        existing_service_ids = set(
            db.scalars(select(Service.id).where(Service.id.in_(service_ids))).all()
        )
        missing_service_ids = [
            service_id
            for service_id in service_ids
            if service_id not in existing_service_ids
        ]
        if missing_service_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Services not found: {missing_service_ids}",
            )

    master_data = data.model_dump(exclude={"service_ids"})
    master = Master(**master_data)
    master.service_links = [
        MasterService(service_id=service_id)
        for service_id in service_ids
    ]

    db.add(master)
    db.commit()
    db.refresh(master)

    logger.info(
        "[MASTERS] Master created: master_id=%s name=%s %s",
        master.id,
        master.first_name,
        master.last_name,
    )

    statement = (
        select(Master)
        .where(Master.id == master.id)
        .options(selectinload(Master.service_links).selectinload(MasterService.service))
    )
    return db.scalars(statement).one()
