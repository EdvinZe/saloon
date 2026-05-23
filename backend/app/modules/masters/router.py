from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.masters.schemas import MasterPublic
from app.modules.masters.service import list_public_masters

router = APIRouter()


@router.get("/public", response_model=list[MasterPublic])
def get_public_masters(
    service_id: int | None = None,
    db: Session = Depends(get_db),
):
    return list_public_masters(db, service_id=service_id)
