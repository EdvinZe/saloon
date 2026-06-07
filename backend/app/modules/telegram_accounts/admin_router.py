from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.telegram_accounts.schemas import (
    TelegramAccountCreate,
    TelegramAccountRead,
    TelegramAccountUpdate,
)
from app.modules.telegram_accounts.service import (
    activate_admin_telegram_account,
    create_admin_telegram_account,
    deactivate_admin_telegram_account,
    get_admin_telegram_account,
    list_admin_telegram_accounts,
    update_admin_telegram_account,
)

router = APIRouter()


@router.get("", response_model=list[TelegramAccountRead])
def get_admin_telegram_accounts(db: Session = Depends(get_db)):
    return list_admin_telegram_accounts(db)


@router.get("/{account_id}", response_model=TelegramAccountRead)
def get_admin_telegram_account_route(
    account_id: int,
    db: Session = Depends(get_db),
):
    return get_admin_telegram_account(db, account_id)


@router.post("", response_model=TelegramAccountRead, status_code=status.HTTP_201_CREATED)
def create_admin_telegram_account_route(
    data: TelegramAccountCreate,
    db: Session = Depends(get_db),
):
    return create_admin_telegram_account(db, data)


@router.patch("/{account_id}", response_model=TelegramAccountRead)
def update_admin_telegram_account_route(
    account_id: int,
    data: TelegramAccountUpdate,
    db: Session = Depends(get_db),
):
    return update_admin_telegram_account(db, account_id, data)


@router.post("/{account_id}/activate", response_model=TelegramAccountRead)
def activate_admin_telegram_account_route(
    account_id: int,
    db: Session = Depends(get_db),
):
    return activate_admin_telegram_account(db, account_id)


@router.post("/{account_id}/deactivate", response_model=TelegramAccountRead)
def deactivate_admin_telegram_account_route(
    account_id: int,
    db: Session = Depends(get_db),
):
    return deactivate_admin_telegram_account(db, account_id)
