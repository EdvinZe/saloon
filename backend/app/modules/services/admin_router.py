from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.services.schemas import ServiceAdmin, ServiceCreate
from app.modules.services.service import create_service

router = APIRouter()


@router.post("/", response_model=ServiceAdmin, status_code=status.HTTP_201_CREATED)
def create_admin_service(data: ServiceCreate, db: Session = Depends(get_db)):
    return create_service(db, data)
