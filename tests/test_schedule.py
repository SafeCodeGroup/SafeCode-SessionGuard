import datetime

import pytest

from sessionguard.schedule import describe, in_schedule, parse_hhmm

T = parse_hhmm
WEEKDAYS = [0, 1, 2, 3, 4]
MON = datetime.date(2026, 10, 12)  # a Monday


def at(day_offset, hhmm):
    return datetime.datetime.combine(MON + datetime.timedelta(days=day_offset), T(hhmm))


@pytest.mark.parametrize(
    "when,expected",
    [
        (at(0, "08:59"), False),
        (at(0, "09:00"), True),
        (at(0, "17:59"), True),
        (at(0, "18:00"), False),
        (at(5, "12:00"), False),  # Saturday
    ],
)
def test_day_window(when, expected):
    assert in_schedule(when, T("09:00"), T("18:00"), WEEKDAYS) is expected


@pytest.mark.parametrize(
    "when,expected",
    [
        (at(4, "23:00"), True),  # Friday night shift
        (at(5, "05:00"), True),  # ...continues into Saturday morning
        (at(5, "23:00"), False),  # Saturday shift not scheduled
        (at(0, "05:00"), False),  # Monday 05:00 belongs to Sunday's shift
        (at(0, "12:00"), False),
    ],
)
def test_overnight_window(when, expected):
    assert in_schedule(when, T("22:00"), T("06:00"), WEEKDAYS) is expected


def test_equal_start_end_means_all_day():
    assert in_schedule(at(0, "03:00"), T("00:00"), T("00:00"), [0])
    assert not in_schedule(at(1, "03:00"), T("00:00"), T("00:00"), [0])


def test_describe():
    assert describe("09:00", "18:00", WEEKDAYS) == "09:00–18:00, Mon–Fri"
    assert describe("09:00", "18:00", list(range(7))) == "09:00–18:00, every day"
    assert describe("09:00", "18:00", [0, 2]) == "09:00–18:00, Mon, Wed"
