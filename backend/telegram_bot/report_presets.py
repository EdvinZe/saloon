from datetime import date, timedelta


def get_today_range() -> tuple[str, str]:
    today = date.today()
    return today.isoformat(), today.isoformat()


def get_yesterday_range() -> tuple[str, str]:
    yesterday = date.today() - timedelta(days=1)
    return yesterday.isoformat(), yesterday.isoformat()


def get_this_week_range() -> tuple[str, str]:
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    return monday.isoformat(), today.isoformat()


def get_last_week_range() -> tuple[str, str]:
    today = date.today()
    this_monday = today - timedelta(days=today.weekday())
    last_monday = this_monday - timedelta(days=7)
    last_sunday = this_monday - timedelta(days=1)
    return last_monday.isoformat(), last_sunday.isoformat()


def get_this_month_range() -> tuple[str, str]:
    today = date.today()
    first_day = today.replace(day=1)
    return first_day.isoformat(), today.isoformat()


def get_last_month_range() -> tuple[str, str]:
    today = date.today()
    first_this_month = today.replace(day=1)
    last_month_end = first_this_month - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)
    return last_month_start.isoformat(), last_month_end.isoformat()
