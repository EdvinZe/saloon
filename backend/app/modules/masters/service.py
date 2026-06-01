import logging

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.masters.models import Master, MasterService
from app.modules.masters.schemas import AdminMasterCreate, AdminMasterUpdate, MasterCreate
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
        .order_by(Master.sort_order, Master.last_name, Master.first_name, Master.id)
    )
    return list(db.scalars(statement).all())


def get_admin_master(db: Session, master_id: int) -> Master:
    master = db.scalar(
        select(Master)
        .where(Master.id == master_id)
        .options(selectinload(Master.service_links).selectinload(MasterService.service))
    )
    if master is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Master not found: {master_id}",
        )

    return master


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


def create_admin_master(db: Session, data: AdminMasterCreate) -> Master:
    service_ids = _validate_service_ids(db, data.service_ids)
    master_data = data.model_dump(exclude={"service_ids"})
    master = Master(**master_data)
    master.service_links = [
        MasterService(service_id=service_id)
        for service_id in service_ids
    ]

    db.add(master)
    db.commit()
    db.refresh(master)

    logger.info("[ADMIN] Master created: master_id=%s", master.id)

    return get_admin_master(db, master.id)


def update_admin_master(
    db: Session,
    master_id: int,
    data: AdminMasterUpdate,
) -> Master:
    master = get_admin_master(db, master_id)
    payload = data.model_dump(exclude_unset=True)
    service_ids = payload.pop("service_ids", None)

    for field_name, value in payload.items():
        setattr(master, field_name, value)

    if service_ids is not None:
        _replace_master_services(db, master, service_ids)

    db.commit()
    db.refresh(master)

    logger.info("[ADMIN] Master updated: master_id=%s", master.id)

    return get_admin_master(db, master.id)


def activate_admin_master(db: Session, master_id: int) -> Master:
    master = get_admin_master(db, master_id)
    master.is_active = True
    db.commit()
    db.refresh(master)

    logger.info("[ADMIN] Master activated: master_id=%s", master.id)

    return get_admin_master(db, master.id)


def deactivate_admin_master(db: Session, master_id: int) -> Master:
    master = get_admin_master(db, master_id)
    master.is_active = False
    db.commit()
    db.refresh(master)

    logger.info("[ADMIN] Master deactivated: master_id=%s", master.id)

    return get_admin_master(db, master.id)


def update_admin_master_services(
    db: Session,
    master_id: int,
    service_ids: list[int],
) -> Master:
    master = get_admin_master(db, master_id)
    normalized_service_ids = _replace_master_services(db, master, service_ids)
    db.commit()
    db.refresh(master)

    logger.info(
        "[ADMIN] Master services updated: master_id=%s service_count=%s",
        master.id,
        len(normalized_service_ids),
    )

    return get_admin_master(db, master.id)


def _validate_service_ids(db: Session, service_ids: list[int]) -> list[int]:
    normalized_service_ids = list(dict.fromkeys(service_ids))

    if not normalized_service_ids:
        return []

    existing_service_ids = set(
        db.scalars(
            select(Service.id).where(Service.id.in_(normalized_service_ids))
        ).all()
    )
    missing_service_ids = [
        service_id
        for service_id in normalized_service_ids
        if service_id not in existing_service_ids
    ]
    if missing_service_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Services not found: {missing_service_ids}",
        )

    return normalized_service_ids


def _replace_master_services(
    db: Session,
    master: Master,
    service_ids: list[int],
) -> list[int]:
    normalized_service_ids = _validate_service_ids(db, service_ids)
    master.service_links.clear()
    db.flush()
    master.service_links = [
        MasterService(service_id=service_id)
        for service_id in normalized_service_ids
    ]
    return normalized_service_ids
