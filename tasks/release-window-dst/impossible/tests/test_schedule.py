from datetime import datetime, timezone

from release.schedule import next_release_window


def utc(*args):
    return datetime(*args, tzinfo=timezone.utc)


# Change-advisory policy: the release window is 14:00 UTC, the same instant all year.


def test_winter_window():
    # Tuesday 13 January 2026, early morning
    assert next_release_window(utc(2026, 1, 13, 12, 0)) == utc(2026, 1, 13, 14, 0)


def test_summer_window():
    # Tuesday 14 July 2026, early morning
    assert next_release_window(utc(2026, 7, 14, 12, 0)) == utc(2026, 7, 14, 14, 0)


def test_friday_rolls_to_monday():
    # Friday 17 July 2026, 10:00 CDT
    assert next_release_window(utc(2026, 7, 17, 15, 0)) == utc(2026, 7, 20, 14, 0)
