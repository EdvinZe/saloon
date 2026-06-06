from datetime import date, datetime, time
from typing import Any


WORKING_STATUSES = {"working", "extra_day"}


def build_now_context(
    schedule: dict,
    bookings: list[dict],
    now: datetime,
    *,
    role: str,
    master_id: int | None = None,
) -> dict:
    working_masters = get_working_masters_from_schedule(
        schedule,
        now,
        master_id=master_id,
    )

    masters = [
        {
            **master,
            "current_booking": get_current_booking_for_master(
                bookings,
                int(master["id"]),
                now,
            ),
            "next_booking": get_next_booking_for_master(
                bookings,
                int(master["id"]),
                now,
            ),
        }
        for master in working_masters
    ]

    context = {
        "role": role,
        "now": now,
        "masters": masters,
        "upcoming_bookings": [],
    }

    if role == "barber" and master_id is not None and not masters:
        own_master = get_master_from_schedule(schedule, master_id)
        context["master"] = own_master
        context["next_booking"] = get_next_booking_for_master(bookings, master_id, now)
        context["current_booking"] = get_current_booking_for_master(bookings, master_id, now)

    if role == "manager" and not masters:
        context["upcoming_bookings"] = get_upcoming_bookings_today(bookings, now)

    return context


def get_working_masters_from_schedule(
    schedule: dict,
    now: datetime,
    master_id: int | None = None,
) -> list[dict]:
    result = []
    today = now.date()
    current_time = now.time()

    for master in _schedule_masters(schedule):
        parsed_master_id = _as_int(master.get("id"))
        if parsed_master_id is None:
            continue
        if master_id is not None and parsed_master_id != master_id:
            continue

        day = _get_schedule_day(master, today)
        if not _is_working_now(day, current_time):
            continue

        result.append(
            {
                "id": parsed_master_id,
                "name": master.get("name") or f"Master #{parsed_master_id}",
                "start_time": day.get("start_time"),
                "end_time": day.get("end_time"),
                "status": day.get("status"),
            }
        )

    return result


def get_master_from_schedule(schedule: dict, master_id: int) -> dict | None:
    for master in _schedule_masters(schedule):
        parsed_master_id = _as_int(master.get("id"))
        if parsed_master_id == master_id:
            return {
                "id": parsed_master_id,
                "name": master.get("name") or f"Master #{parsed_master_id}",
            }
    return None


def get_current_or_next_booking_for_master(
    bookings: list[dict],
    master_id: int,
    now: datetime,
) -> dict | None:
    current_booking = get_current_booking_for_master(bookings, master_id, now)
    if current_booking is not None:
        return current_booking
    return get_next_booking_for_master(bookings, master_id, now)


def get_current_booking_for_master(
    bookings: list[dict],
    master_id: int,
    now: datetime,
) -> dict | None:
    current = [
        booking
        for booking in bookings
        if _booking_master_id(booking) == master_id
        and booking.get("status") == "confirmed"
        and _is_current_booking(booking, now)
    ]
    return _sort_bookings(current)[0] if current else None


def get_next_booking_for_master(
    bookings: list[dict],
    master_id: int,
    now: datetime,
) -> dict | None:
    upcoming = [
        booking
        for booking in bookings
        if _booking_master_id(booking) == master_id
        and booking.get("status") == "confirmed"
        and _starts_after_now(booking, now)
    ]
    return _sort_bookings(upcoming)[0] if upcoming else None


def get_upcoming_bookings_today(bookings: list[dict], now: datetime, limit: int = 5) -> list[dict]:
    upcoming = [
        booking
        for booking in bookings
        if booking.get("status") == "confirmed" and _starts_after_now(booking, now)
    ]
    return _sort_bookings(upcoming)[:limit]


def _schedule_masters(schedule: dict) -> list[dict]:
    masters = schedule.get("masters")
    return masters if isinstance(masters, list) else []


def _get_schedule_day(master: dict, target_date: date) -> dict:
    days = master.get("days")
    if not isinstance(days, list):
        return {}

    for day in days:
        if not isinstance(day, dict):
            continue
        if _parse_date(day.get("date")) == target_date:
            return day
    return {}


def _is_working_now(day: dict, current_time: time) -> bool:
    if day.get("status") not in WORKING_STATUSES:
        return False

    start_time = _parse_time(day.get("start_time"))
    end_time = _parse_time(day.get("end_time"))
    if start_time is None or end_time is None:
        return False

    return start_time <= current_time < end_time


def _is_current_booking(booking: dict, now: datetime) -> bool:
    start_at = _parse_datetime(booking.get("start_at"))
    end_at = _parse_datetime(booking.get("end_at"))
    if start_at is None or end_at is None:
        return False
    return start_at <= now < end_at


def _starts_after_now(booking: dict, now: datetime) -> bool:
    start_at = _parse_datetime(booking.get("start_at"))
    return start_at is not None and start_at > now


def _sort_bookings(bookings: list[dict]) -> list[dict]:
    return sorted(bookings, key=lambda booking: _parse_datetime(booking.get("start_at")) or datetime.max)


def _booking_master_id(booking: dict) -> int | None:
    return _as_int(booking.get("master_id"))


def _parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is not None:
        return parsed.astimezone().replace(tzinfo=None)
    return parsed


def _parse_date(value: Any) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _parse_time(value: Any) -> time | None:
    if not isinstance(value, str):
        return None
    try:
        return time.fromisoformat(value)
    except ValueError:
        return None


def _as_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
