"""Active-hours window: only keep the session alive at certain times."""

import datetime

DAY_NAMES = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")


def parse_hhmm(value: str) -> datetime.time:
    """Parse "HH:MM" (24-hour). Raises ValueError on bad input."""
    return datetime.datetime.strptime(value, "%H:%M").time()


def in_schedule(now: datetime.datetime, start: datetime.time, end: datetime.time, days) -> bool:
    """True if `now` is inside the window on one of `days` (0 = Monday).

    A window that ends before it starts (e.g. 22:00-06:00) runs overnight;
    the early-morning part belongs to the previous day's shift.
    """
    t = now.time()
    weekday = now.weekday()
    if start == end:
        return weekday in days
    if start < end:
        return weekday in days and start <= t < end
    if t >= start:
        return weekday in days
    if t < end:
        return (weekday - 1) % 7 in days
    return False


def describe_days(days) -> str:
    days = sorted(set(days))
    if days == [0, 1, 2, 3, 4, 5, 6]:
        return "every day"
    if days == [0, 1, 2, 3, 4]:
        return "Mon–Fri"
    if days == [5, 6]:
        return "Sat–Sun"
    return ", ".join(DAY_NAMES[d] for d in days) or "no days"


def describe(start: str, end: str, days) -> str:
    return f"{start}–{end}, {describe_days(days)}"
