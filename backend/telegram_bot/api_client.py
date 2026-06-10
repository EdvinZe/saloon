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


async def get_admin_bookings(
    date: str,
    status: str = "confirmed",
    master_id: int | None = None,
) -> list[dict]:
    params: dict[str, str | int] = {"date": date, "status": status}
    if master_id is not None:
        params["master_id"] = master_id

    payload = await _request(
        "GET",
        "/api/admin/bookings",
        params=params,
    )
    if not isinstance(payload, list):
        raise BackendAPIError("Backend returned an invalid bookings response.")
    return payload


async def resolve_telegram_account(telegram_id: int) -> dict:
    payload = await _request(
        "GET",
        "/api/bot/telegram-accounts/resolve",
        params={"telegram_id": telegram_id},
    )
    if not isinstance(payload, dict):
        raise BackendAPIError("Backend returned an invalid Telegram account response.")
    return payload


async def get_barber_telegram_ids_by_master(master_id: int) -> list[int]:
    payload = await _request(
        "GET",
        f"/api/bot/telegram-accounts/barbers/by-master/{master_id}",
    )
    if not isinstance(payload, dict):
        raise BackendAPIError("Backend returned an invalid barber routing response.")

    telegram_ids = payload.get("telegram_ids")
    if not isinstance(telegram_ids, list):
        raise BackendAPIError("Backend returned an invalid barber routing response.")

    result: list[int] = []
    for telegram_id in telegram_ids:
        try:
            result.append(int(telegram_id))
        except (TypeError, ValueError):
            continue
    return result


async def get_admin_schedule(from_date: str, to_date: str) -> dict:
    payload = await _request(
        "GET",
        "/api/admin/schedule/",
        params={"from_date": from_date, "to_date": to_date},
    )
    if not isinstance(payload, dict):
        raise BackendAPIError("Backend returned an invalid schedule response.")
    return payload


async def get_admin_report_summary(
    from_date: str,
    to_date: str,
    master_id: int | None = None,
) -> dict:
    params: dict[str, str | int] = {
        "from_date": from_date,
        "to_date": to_date,
    }
    if master_id is not None:
        params["master_id"] = master_id

    payload = await _request(
        "GET",
        "/api/admin/reports/summary",
        params=params,
    )
    if not isinstance(payload, dict):
        raise BackendAPIError("Backend returned an invalid report response.")
    return payload


async def get_admin_booking(booking_id: int) -> dict:
    payload = await _request("GET", f"/api/admin/bookings/{booking_id}")
    if not isinstance(payload, dict):
        raise BackendAPIError("Backend returned an invalid booking response.")
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
