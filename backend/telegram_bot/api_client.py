from typing import Any

import httpx

from telegram_bot.config import load_config


class BackendAPIError(Exception):
    """Raised when the backend API cannot satisfy a bot request."""


def _extract_error_detail(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return response.reason_phrase or "Backend request failed"

    detail = payload.get("detail") if isinstance(payload, dict) else None
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list):
        return "Backend validation failed"
    return payload.get("message", "Backend request failed") if isinstance(payload, dict) else "Backend request failed"


async def _request(method: str, path: str, **kwargs: Any) -> Any:
    config = load_config()
    url = f"{config.backend_api_url}{path}"
    timeout = httpx.Timeout(10.0)

    # TODO: When admin auth is enabled, send ADMIN_API_TOKEN as an auth header.
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(method, url, **kwargs)
    except httpx.TimeoutException as exc:
        raise BackendAPIError("Backend is unavailable. Please try again later.") from exc
    except httpx.HTTPError as exc:
        raise BackendAPIError("Backend is unavailable. Please try again later.") from exc

    if response.is_error:
        detail = _extract_error_detail(response)
        raise BackendAPIError(detail)

    try:
        return response.json()
    except ValueError as exc:
        raise BackendAPIError("Backend returned an invalid response.") from exc


async def get_admin_bookings(date: str, status: str = "confirmed") -> list[dict]:
    payload = await _request(
        "GET",
        "/api/admin/bookings",
        params={"date": date, "status": status},
    )
    if not isinstance(payload, list):
        raise BackendAPIError("Backend returned an invalid bookings response.")
    return payload


async def complete_booking(booking_id: int) -> dict:
    payload = await _request("POST", f"/api/admin/bookings/{booking_id}/complete")
    if not isinstance(payload, dict):
        raise BackendAPIError("Backend returned an invalid action response.")
    return payload


async def mark_booking_no_show(booking_id: int) -> dict:
    payload = await _request("POST", f"/api/admin/bookings/{booking_id}/no-show")
    if not isinstance(payload, dict):
        raise BackendAPIError("Backend returned an invalid action response.")
    return payload
