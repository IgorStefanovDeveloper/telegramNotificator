"""Timezone helpers: store events in UTC, display in user TZ."""
from datetime import datetime, timezone

import pytz


def local_to_utc(dt_naive: datetime, tz_str: str) -> datetime:
    """Convert naive datetime (in user's TZ) to UTC naive."""
    tz = pytz.timezone(tz_str)
    local = tz.localize(dt_naive)
    utc = local.astimezone(timezone.utc)
    return utc.replace(tzinfo=None)  # Return naive UTC for storage


def utc_to_local(dt_utc_naive: datetime, tz_str: str) -> datetime:
    """Convert stored UTC (naive) to local naive for display."""
    utc = dt_utc_naive.replace(tzinfo=timezone.utc)
    local = utc.astimezone(pytz.timezone(tz_str))
    return local.replace(tzinfo=None)


def format_utc_for_display(dt_utc_naive: datetime, tz_str: str) -> str:
    """Format UTC-stored datetime for display in user TZ."""
    local = utc_to_local(dt_utc_naive, tz_str)
    return local.strftime("%d.%m.%Y %H:%M")


def utc_now() -> datetime:
    """Current time in UTC (naive)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
