from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.telegram_accounts.schemas import (
    BotTelegramAccountResolve,
    BotTelegramBarbersByMaster,
)
from app.modules.telegram_accounts.service import (
    list_active_barber_telegram_ids_by_master,
    resolve_telegram_account,
)

router = APIRouter()


@router.get("/resolve", response_model=BotTelegramAccountResolve)
def resolve_telegram_account_route(
    telegram_id: int,
    db: Session = Depends(get_db),
):
    return resolve_telegram_account(db, telegram_id)


@router.get("/barbers/by-master/{master_id}", response_model=BotTelegramBarbersByMaster)
def get_barbers_by_master_route(
    master_id: int,
    db: Session = Depends(get_db),
):
    return BotTelegramBarbersByMaster(
        master_id=master_id,
        telegram_ids=list_active_barber_telegram_ids_by_master(db, master_id),
    )
