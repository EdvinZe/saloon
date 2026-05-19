from fastapi import APIRouter

from app.modules.services.schemas import ServicePublic
from app.modules.services.service import get_public_services

router = APIRouter()


@router.get("/public", response_model=list[ServicePublic])
def list_public_services():
    return get_public_services()