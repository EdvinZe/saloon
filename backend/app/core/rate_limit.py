from dataclasses import dataclass
import time

from starlette.types import ASGIApp, Receive, Scope, Send

from app.core import config


@dataclass(frozen=True)
class RateLimitRule:
    bucket: str
    limit: int
    window_seconds: int


PUBLIC_RATE_LIMIT = RateLimitRule(bucket="public", limit=120, window_seconds=60)
AVAILABILITY_RATE_LIMIT = RateLimitRule(
    bucket="availability",
    limit=120,
    window_seconds=60,
)
PAYMENT_RATE_LIMIT = RateLimitRule(bucket="payment", limit=20, window_seconds=60)
MANAGE_RATE_LIMIT = RateLimitRule(bucket="manage", limit=10, window_seconds=60)
TELEGRAM_RATE_LIMIT = RateLimitRule(bucket="telegram", limit=60, window_seconds=60)
ADMIN_LOGIN_RATE_LIMIT = RateLimitRule(
    bucket="admin_login",
    limit=5,
    window_seconds=300,
)


@dataclass
class _Window:
    count: int
    reset_at: float


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._windows: dict[tuple[str, str], _Window] = {}

    def allow(self, key: str, bucket: str, limit: int, window_seconds: int) -> bool:
        if limit <= 0:
            return False

        now = time.monotonic()
        self._cleanup(now)

        window_key = (bucket, key)
        window = self._windows.get(window_key)
        if window is None or window.reset_at <= now:
            self._windows[window_key] = _Window(
                count=1,
                reset_at=now + max(1, window_seconds),
            )
            return True

        if window.count >= limit:
            return False

        window.count += 1
        return True

    def reset(self, key: str, bucket: str) -> None:
        self._windows.pop((bucket, key), None)

    def clear(self) -> None:
        self._windows.clear()

    def _cleanup(self, now: float) -> None:
        expired_keys = [
            window_key
            for window_key, window in self._windows.items()
            if window.reset_at <= now
        ]
        for window_key in expired_keys:
            self._windows.pop(window_key, None)


rate_limiter = InMemoryRateLimiter()
admin_login_limiter = InMemoryRateLimiter()


def client_ip_from_scope(scope: Scope) -> str:
    client = scope.get("client")
    if isinstance(client, tuple) and client:
        return str(client[0])
    return "unknown"


def client_ip_from_request(request) -> str:
    host = getattr(getattr(request, "client", None), "host", None)
    return str(host or "unknown")


def rate_limit_rule_for_request(path: str, method: str) -> RateLimitRule | None:
    normalized_method = method.upper()

    if normalized_method == "GET" and path in {
        "/api/services/public",
        "/api/masters/public",
    }:
        return PUBLIC_RATE_LIMIT

    if normalized_method == "GET" and path in {
        "/api/availability/slots",
        "/api/availability/masters",
    }:
        return AVAILABILITY_RATE_LIMIT

    if path in {
        "/api/bookings/deposit-intent",
        "/api/bookings/payment-result",
    }:
        return PAYMENT_RATE_LIMIT

    if path in {
        "/api/bookings/manage",
        "/api/bookings/manage/cancel",
        "/api/bookings/manage/reschedule",
    }:
        return MANAGE_RATE_LIMIT

    if path.startswith("/api/bot/"):
        return TELEGRAM_RATE_LIMIT

    return None


class RateLimitMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or not config.RATE_LIMIT_ENABLED:
            await self.app(scope, receive, send)
            return

        rule = rate_limit_rule_for_request(
            path=str(scope.get("path", "")),
            method=str(scope.get("method", "")),
        )
        if rule is None:
            await self.app(scope, receive, send)
            return

        key = client_ip_from_scope(scope)
        if rate_limiter.allow(key, rule.bucket, rule.limit, rule.window_seconds):
            await self.app(scope, receive, send)
            return

        await _send_rate_limited_response(send)


async def _send_rate_limited_response(send: Send) -> None:
    body = b'{"detail":"Rate limit exceeded. Please try again later."}'
    await send(
        {
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode("ascii")),
            ],
        }
    )
    await send({"type": "http.response.body", "body": body})
