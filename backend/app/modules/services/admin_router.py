from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.services.schemas import (
    AdminServiceCreate,
    AdminServiceRead,
    AdminServiceUpdate,
)
from app.modules.services.service import (
    activate_admin_service,
    create_admin_service,
    deactivate_admin_service,
    get_admin_service,
    list_admin_services,
    update_admin_service,
)

router = APIRouter()


@router.get("", response_model=list[AdminServiceRead])
def get_admin_services(db: Session = Depends(get_db)):
    return list_admin_services(db)


@router.get("/{service_id}", response_model=AdminServiceRead)
def get_admin_service_route(service_id: int, db: Session = Depends(get_db)):
    return get_admin_service(db, service_id)


@router.post("", response_model=AdminServiceRead, status_code=status.HTTP_201_CREATED)
def create_admin_service_route(
    data: AdminServiceCreate,
    db: Session = Depends(get_db),
):
    return create_admin_service(db, data)


@router.patch("/{service_id}", response_model=AdminServiceRead)
def update_admin_service_route(
    service_id: int,
    data: AdminServiceUpdate,
    db: Session = Depends(get_db),
):
    return update_admin_service(db, service_id, data)


@router.post("/{service_id}/activate", response_model=AdminServiceRead)
def activate_admin_service_route(service_id: int, db: Session = Depends(get_db)):
    return activate_admin_service(db, service_id)


@router.post("/{service_id}/deactivate", response_model=AdminServiceRead)
def deactivate_admin_service_route(service_id: int, db: Session = Depends(get_db)):
    return deactivate_admin_service(db, service_id)
