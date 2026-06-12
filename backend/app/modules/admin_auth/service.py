import hashlib
import hmac
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import HTTPException, Request, status

from app.core.config import (
    ADMIN_PASSWORD,
    ADMIN_PASSWORD_HASH,
    ADMIN_SESSION_EXPIRE_MINUTES,
    ADMIN_USERNAME,
    get_admin_session_secret,
)

logger = logging.getLogger(__name__)

ADMIN_SESSION_COOKIE = "admin_session"
ADMIN_ROLE = "manager"
JWT_ALGORITHM = "HS256"


@dataclass(frozen=True)
class AdminUserContext:
    username: str
    role: str = ADMIN_ROLE


def authenticate_admin(username: str, password: str) -> AdminUserContext | None:
    configured_username = ADMIN_USERNAME
    if not configured_username:
        logger.warning("[ADMIN_AUTH] Login unavailable: admin username missing")
        return None

    if not hmac.compare_digest(username, configured_username):
        return None

    if ADMIN_PASSWORD_HASH:
        if _verify_password_hash(password, ADMIN_PASSWORD_HASH):
            return AdminUserContext(username=configured_username)
        return None

    if ADMIN_PASSWORD and hmac.compare_digest(password, ADMIN_PASSWORD):
        return AdminUserContext(username=configured_username)

    logger.warning("[ADMIN_AUTH] Login unavailable: admin password missing")
    return None


def create_admin_session_token(user: AdminUserContext) -> str:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=max(1, ADMIN_SESSION_EXPIRE_MINUTES))
    payload = {
        "sub": user.username,
        "role": user.role,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    return jwt.encode(payload, get_admin_session_secret(), algorithm=JWT_ALGORITHM)


def get_admin_user_from_request(request: Request) -> AdminUserContext | None:
    token = request.cookies.get(ADMIN_SESSION_COOKIE)
    if not token:
        return None

    try:
        payload = jwt.decode(
            token,
            get_admin_session_secret(),
            algorithms=[JWT_ALGORITHM],
        )
    except jwt.PyJWTError:
        return None

    username = _payload_text(payload, "sub")
    role = _payload_text(payload, "role")
    if not username or role != ADMIN_ROLE:
        return None

    return AdminUserContext(username=username, role=role)


def require_admin_user(request: Request) -> AdminUserContext:
    user = get_admin_user_from_request(request)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication required",
        )
    return user


def _verify_password_hash(password: str, password_hash: str) -> bool:
    normalized = password_hash.strip()
    if normalized.startswith("sha256$"):
        expected = normalized.removeprefix("sha256$")
        actual = hashlib.sha256(password.encode("utf-8")).hexdigest()
        return hmac.compare_digest(actual, expected)
    return False


def _payload_text(payload: dict[str, Any], key: str) -> str | None:
    value = payload.get(key)
    if not isinstance(value, str):
        return None
    value = value.strip()
    return value or None
