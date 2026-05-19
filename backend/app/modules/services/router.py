from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.services.schemas import ServicePublic
from app.modules.services.service import list_public_services

router = APIRouter()


@router.get("/public", response_model=list[ServicePublic])
def get_public_services(db: Session = Depends(get_db)):
    return list_public_services(db)
