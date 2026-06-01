from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.masters.schemas import (
    AdminMasterCreate,
    AdminMasterRead,
    AdminMasterServicesUpdate,
    AdminMasterUpdate,
)
from app.modules.masters.service import (
    activate_admin_master,
    create_admin_master,
    deactivate_admin_master,
    get_admin_master,
    list_admin_masters,
    update_admin_master,
    update_admin_master_services,
)

router = APIRouter()


@router.get("", response_model=list[AdminMasterRead])
def get_admin_masters(db: Session = Depends(get_db)):
    return list_admin_masters(db)


@router.get("/{master_id}", response_model=AdminMasterRead)
def get_admin_master_route(master_id: int, db: Session = Depends(get_db)):
    return get_admin_master(db, master_id)


@router.post("", response_model=AdminMasterRead, status_code=status.HTTP_201_CREATED)
def create_admin_master_route(
    data: AdminMasterCreate,
    db: Session = Depends(get_db),
):
    return create_admin_master(db, data)


@router.patch("/{master_id}", response_model=AdminMasterRead)
def update_admin_master_route(
    master_id: int,
    data: AdminMasterUpdate,
    db: Session = Depends(get_db),
):
    return update_admin_master(db, master_id, data)


@router.post("/{master_id}/activate", response_model=AdminMasterRead)
def activate_admin_master_route(master_id: int, db: Session = Depends(get_db)):
    return activate_admin_master(db, master_id)


@router.post("/{master_id}/deactivate", response_model=AdminMasterRead)
def deactivate_admin_master_route(master_id: int, db: Session = Depends(get_db)):
    return deactivate_admin_master(db, master_id)


@router.put("/{master_id}/services", response_model=AdminMasterRead)
def update_admin_master_services_route(
    master_id: int,
    data: AdminMasterServicesUpdate,
    db: Session = Depends(get_db),
):
    return update_admin_master_services(db, master_id, data.service_ids)
