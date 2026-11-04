from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from release.schedule import next_release_window


def utc(*args):
    return datetime(*args, tzinfo=timezone.utc)


@pytest.mark.parametrize("now,expected", [
    # Friday before spring-forward (Sun 8 Mar 2026) -> Monday 09:00 CDT
    (utc(2026, 3, 6, 18, 0), utc(2026, 3, 9, 14, 0)),
    # Thursday after the window, before fall-back (Sun 1 Nov 2026) -> Monday 09:00 CST
    (utc(2026, 10, 29, 16, 0), utc(2026, 11, 2, 15, 0)),
    # Winter and summer, before the window
    (utc(2026, 1, 13, 14, 0), utc(2026, 1, 13, 15, 0)),
    (utc(2026, 7, 14, 13, 0), utc(2026, 7, 14, 14, 0)),
    # Saturday and Sunday roll to Monday
    (utc(2026, 7, 18, 12, 0), utc(2026, 7, 20, 14, 0)),
    (utc(2026, 12, 13, 12, 0), utc(2026, 12, 14, 15, 0)),
])
def test_windows_across_the_year(now, expected):
    assert next_release_window(now) == expected


def test_exactly_at_window_returns_it():
    assert next_release_window(utc(2026, 7, 14, 14, 0)) == utc(2026, 7, 14, 14, 0)
    assert next_release_window(utc(2026, 1, 13, 15, 0)) == utc(2026, 1, 13, 15, 0)


def test_just_after_window_moves_to_next_day():
    after = utc(2026, 7, 14, 14, 0) + timedelta(microseconds=1)
    assert next_release_window(after) == utc(2026, 7, 15, 14, 0)


def test_thursday_after_window_rolls_to_monday():
    assert next_release_window(utc(2026, 1, 15, 16, 0)) == utc(2026, 1, 19, 15, 0)


def test_input_in_another_zone():
    tokyo = datetime(2026, 7, 14, 22, 0, tzinfo=ZoneInfo("Asia/Tokyo"))  # 13:00 UTC
    assert next_release_window(tokyo) == utc(2026, 7, 14, 14, 0)


def test_result_is_utc():
    result = next_release_window(utc(2026, 7, 14, 13, 0))
    assert result.utcoffset() == timedelta(0)
