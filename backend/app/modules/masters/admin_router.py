from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.masters.schemas import MasterAdmin, MasterCreate
from app.modules.masters.service import create_master, list_admin_masters

router = APIRouter()


@router.get("/", response_model=list[MasterAdmin])
def get_admin_masters(db: Session = Depends(get_db)):
    return list_admin_masters(db)


@router.post("/", response_model=MasterAdmin, status_code=status.HTTP_201_CREATED)
def create_admin_master(data: MasterCreate, db: Session = Depends(get_db)):
    return create_master(db, data)
