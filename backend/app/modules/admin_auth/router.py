from fastapi import APIRouter, HTTPException, Request, Response, status

from app.core.config import (
    ADMIN_SESSION_EXPIRE_MINUTES,
    get_cors_allowed_origins,
    is_production,
)
from app.modules.admin_auth.schemas import AdminAuthResponse, AdminLoginRequest
from app.modules.admin_auth.service import (
    ADMIN_ROLE,
    ADMIN_SESSION_COOKIE,
    authenticate_admin,
    create_admin_session_token,
    get_admin_user_from_request,
)

router = APIRouter()


def _admin_cookie_settings() -> dict[str, object]:
    deployed_cross_origin = any(
        origin.startswith("https://")
        and "localhost" not in origin
        and "127.0.0.1" not in origin
        for origin in get_cors_allowed_origins()
    )
    if is_production() or deployed_cross_origin:
        return {"secure": True, "samesite": "none"}
    return {"secure": False, "samesite": "lax"}


@router.post("/login", response_model=AdminAuthResponse)
def login_admin(data: AdminLoginRequest, response: Response):
    user = authenticate_admin(data.username.strip(), data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = create_admin_session_token(user)
    response.set_cookie(
        key=ADMIN_SESSION_COOKIE,
        value=token,
        max_age=max(1, ADMIN_SESSION_EXPIRE_MINUTES) * 60,
        httponly=True,
        **_admin_cookie_settings(),
        path="/",
    )
    return AdminAuthResponse(
        authenticated=True,
        role=user.role,
        username=user.username,
    )


@router.get("/me", response_model=AdminAuthResponse)
def get_current_admin(request: Request):
    user = get_admin_user_from_request(request)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication required",
        )
    return AdminAuthResponse(
        authenticated=True,
        role=user.role,
        username=user.username,
    )


@router.post("/logout", response_model=AdminAuthResponse)
def logout_admin(response: Response):
    response.delete_cookie(
        key=ADMIN_SESSION_COOKIE,
        path="/",
        **_admin_cookie_settings(),
    )
    return AdminAuthResponse(authenticated=False, role=ADMIN_ROLE)
