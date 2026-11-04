"""Release-train scheduling."""

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

RELEASE_HOUR_LOCAL = 9
RELEASE_WEEKDAYS = {0, 1, 2, 3}  # Monday through Thursday
CENTRAL = ZoneInfo("America/Chicago")


def next_release_window(now: datetime) -> datetime:
    """Return the next production release window at or after `now`, in UTC.

    Windows are 09:00 America/Chicago, Monday through Thursday. `now` must be
    timezone-aware.
    """
    local = now.astimezone(CENTRAL)
    candidate = local.replace(hour=RELEASE_HOUR_LOCAL, minute=0, second=0, microsecond=0)
    if candidate < local:
        candidate += timedelta(days=1)
    while candidate.weekday() not in RELEASE_WEEKDAYS:
        candidate += timedelta(days=1)
    # Wall-clock arithmetic above; ZoneInfo picks the right offset for that date.
    return candidate.astimezone(timezone.utc)
