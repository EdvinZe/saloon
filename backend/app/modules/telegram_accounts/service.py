import logging

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.masters.models import Master
from app.modules.telegram_accounts.models import TelegramAccount
from app.modules.telegram_accounts.schemas import (
    BotTelegramAccountResolve,
    TelegramAccountCreate,
    TelegramAccountUpdate,
)

logger = logging.getLogger(__name__)


def list_admin_telegram_accounts(db: Session) -> list[TelegramAccount]:
    statement = (
        select(TelegramAccount)
        .options(selectinload(TelegramAccount.master))
        .order_by(
            TelegramAccount.role,
            TelegramAccount.first_name,
            TelegramAccount.last_name,
            TelegramAccount.id,
        )
    )
    return list(db.scalars(statement).all())


def get_admin_telegram_account(db: Session, account_id: int) -> TelegramAccount:
    account = db.scalar(
        select(TelegramAccount)
        .where(TelegramAccount.id == account_id)
        .options(selectinload(TelegramAccount.master))
    )
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Telegram account not found: {account_id}",
        )

    return account


def create_admin_telegram_account(
    db: Session,
    data: TelegramAccountCreate,
) -> TelegramAccount:
    payload = data.model_dump()
    _validate_role_master(db, payload["role"], payload.get("master_id"))
    _validate_unique_telegram_id(db, payload["telegram_id"])

    account = TelegramAccount(**payload)
    db.add(account)
    db.commit()
    db.refresh(account)

    logger.info(
        "[ADMIN] Telegram account created: account_id=%s role=%s telegram_id=%s",
        account.id,
        account.role,
        account.telegram_id,
    )

    return get_admin_telegram_account(db, account.id)


def update_admin_telegram_account(
    db: Session,
    account_id: int,
    data: TelegramAccountUpdate,
) -> TelegramAccount:
    account = get_admin_telegram_account(db, account_id)
    payload = data.model_dump(exclude_unset=True)

    final_role = payload.get("role", account.role)
    final_master_id = payload.get("master_id", account.master_id)

    _validate_role_master(db, final_role, final_master_id)
    if "telegram_id" in payload and payload["telegram_id"] != account.telegram_id:
        _validate_unique_telegram_id(db, payload["telegram_id"], account_id=account.id)

    for field_name, value in payload.items():
        setattr(account, field_name, value)

    db.commit()
    db.refresh(account)

    logger.info("[ADMIN] Telegram account updated: account_id=%s", account.id)

    return get_admin_telegram_account(db, account.id)


def activate_admin_telegram_account(db: Session, account_id: int) -> TelegramAccount:
    account = get_admin_telegram_account(db, account_id)
    account.is_active = True
    db.commit()
    db.refresh(account)

    logger.info("[ADMIN] Telegram account activated: account_id=%s", account.id)

    return get_admin_telegram_account(db, account.id)


def deactivate_admin_telegram_account(db: Session, account_id: int) -> TelegramAccount:
    account = get_admin_telegram_account(db, account_id)
    account.is_active = False
    db.commit()
    db.refresh(account)

    logger.info("[ADMIN] Telegram account deactivated: account_id=%s", account.id)

    return get_admin_telegram_account(db, account.id)


def resolve_telegram_account(
    db: Session,
    telegram_id: int,
) -> BotTelegramAccountResolve:
    account = db.scalar(
        select(TelegramAccount).where(TelegramAccount.telegram_id == telegram_id)
    )
    if account is None:
        logger.info(
            "[BOT API] Telegram account resolve denied: telegram_id=%s reason=%s",
            telegram_id,
            "not_found",
        )
        return BotTelegramAccountResolve(authorized=False)

    if not account.is_active:
        logger.info(
            "[BOT API] Telegram account resolve denied: telegram_id=%s reason=%s",
            telegram_id,
            "inactive",
        )
        return BotTelegramAccountResolve(authorized=False)

    if account.role == "manager":
        return BotTelegramAccountResolve(
            authorized=True,
            telegram_id=account.telegram_id,
            role="manager",
            scope="all",
            master_id=None,
            first_name=account.first_name,
            last_name=account.last_name,
        )

    if account.role == "barber":
        if account.master_id is None:
            logger.warning(
                "[BOT API] Telegram account resolve denied: telegram_id=%s role=%s reason=%s",
                telegram_id,
                account.role,
                "missing_master_id",
            )
            return BotTelegramAccountResolve(authorized=False)

        return BotTelegramAccountResolve(
            authorized=True,
            telegram_id=account.telegram_id,
            role="barber",
            scope="own_master",
            master_id=account.master_id,
            first_name=account.first_name,
            last_name=account.last_name,
        )

    logger.warning(
        "[BOT API] Telegram account resolve denied: telegram_id=%s role=%s reason=%s",
        telegram_id,
        account.role,
        "invalid_role",
    )
    return BotTelegramAccountResolve(authorized=False)


def list_active_manager_telegram_ids(db: Session) -> list[int]:
    statement = (
        select(TelegramAccount.telegram_id)
        .where(
            TelegramAccount.role == "manager",
            TelegramAccount.is_active.is_(True),
        )
        .order_by(TelegramAccount.id.asc())
    )
    return [int(telegram_id) for telegram_id in db.scalars(statement).all()]


def list_active_barber_telegram_ids_by_master(
    db: Session,
    master_id: int,
) -> list[int]:
    statement = (
        select(TelegramAccount.telegram_id)
        .where(
            TelegramAccount.role == "barber",
            TelegramAccount.master_id == master_id,
            TelegramAccount.is_active.is_(True),
        )
        .order_by(TelegramAccount.id.asc())
    )
    return [int(telegram_id) for telegram_id in db.scalars(statement).all()]


def _validate_role_master(
    db: Session,
    role: str,
    master_id: int | None,
) -> None:
    if role not in {"manager", "barber"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be manager or barber",
        )

    if role == "barber" and master_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="master_id is required for barber accounts",
        )

    if master_id is not None:
        master_exists = db.scalar(select(Master.id).where(Master.id == master_id))
        if master_exists is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Master not found: {master_id}",
            )


def _validate_unique_telegram_id(
    db: Session,
    telegram_id: int,
    account_id: int | None = None,
) -> None:
    statement = select(TelegramAccount.id).where(
        TelegramAccount.telegram_id == telegram_id
    )
    if account_id is not None:
        statement = statement.where(TelegramAccount.id != account_id)

    existing_account_id = db.scalar(statement)
    if existing_account_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Telegram ID already exists: {telegram_id}",
        )
