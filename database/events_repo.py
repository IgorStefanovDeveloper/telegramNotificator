"""Event repository - CRUD and queries. event_datetime stored in UTC."""
from datetime import datetime, timedelta
from typing import Optional

from config import DEFAULT_TIMEZONE, MAX_FUTURE_MONTHS
from utils_timezone import local_to_utc, utc_now
from database.connection import DbConn
from database.models import Event, RECURRENCE_NONE, RECURRENCE_MONTHLY, RECURRENCE_WEEKLY

# Explicit column order for SELECT (no telegram_id)
_EVENT_SELECT = (
    "id, user_id, title, description, event_datetime, timezone, recurrence_type, recurrence_value, "
    "is_completed, notified_at, created_at, is_cancelled, cancelled_at, completed_at, nudge_count"
)
_EVENT_SELECT_E = (
    "e.id, e.user_id, e.title, e.description, e.event_datetime, e.timezone, e.recurrence_type, e.recurrence_value, "
    "e.is_completed, e.notified_at, e.created_at, e.is_cancelled, e.cancelled_at, e.completed_at, e.nudge_count"
)


def _parse_dt(val) -> Optional[datetime]:
    if val is None or val == "":
        return None
    if isinstance(val, datetime):
        return val
    return datetime.fromisoformat(str(val).replace("Z", "+00:00"))


def _row_to_event(row: tuple) -> Event:
    return Event(
        id=row[0],
        user_id=row[1],
        title=row[2],
        description=row[3] or "",
        event_datetime=datetime.fromisoformat(row[4]) if isinstance(row[4], str) else row[4],
        timezone=row[5] or DEFAULT_TIMEZONE,
        recurrence_type=row[6] or RECURRENCE_NONE,
        recurrence_value=row[7] or "",
        is_completed=bool(row[8]),
        created_at=_parse_dt(row[10]) or datetime.now(),
        notified_at=_parse_dt(row[9]),
        is_cancelled=bool(row[11]) if len(row) > 11 else False,
        cancelled_at=_parse_dt(row[12]) if len(row) > 12 else None,
        completed_at=_parse_dt(row[13]) if len(row) > 13 else None,
        nudge_count=int(row[14]) if len(row) > 14 and row[14] is not None else 0,
    )


async def get_or_create_user(conn: DbConn, telegram_id: int) -> int:
    """Get user id by telegram_id, create if not exists. Returns user.id (pk)."""
    row = await conn.fetchone("SELECT id FROM users WHERE telegram_id = ?", (telegram_id,))
    if row:
        return row[0]
    await conn.execute(
        "INSERT INTO users (telegram_id, language, timezone) VALUES (?, 'ru', ?)",
        (telegram_id, DEFAULT_TIMEZONE),
    )
    row = await conn.fetchone("SELECT id FROM users WHERE telegram_id = ?", (telegram_id,))
    return row[0]


async def create_event(
    conn: DbConn,
    user_id: int,
    title: str,
    event_datetime: datetime,
    timezone: str = DEFAULT_TIMEZONE,
    description: Optional[str] = None,
    recurrence_type: str = RECURRENCE_NONE,
    recurrence_value: Optional[str] = None,
) -> int:
    """Create event. event_datetime is local (user TZ); we store UTC."""
    dt_utc = local_to_utc(event_datetime, timezone)
    dt_val = dt_utc.isoformat()
    return await conn.execute_insert_returning_id(
        """INSERT INTO events (user_id, title, description, event_datetime, timezone, recurrence_type, recurrence_value)
           VALUES (?, ?, ?, ?, ?, ?, ?) RETURNING id""",
        (
            user_id,
            title,
            description or "",
            dt_val,
            timezone,
            recurrence_type,
            recurrence_value or "",
        ),
    )


async def get_event_by_id(conn: DbConn, event_id: int) -> Optional[Event]:
    """Get event by id."""
    row = await conn.fetchone(f"SELECT {_EVENT_SELECT} FROM events WHERE id = ?", (event_id,))
    return _row_to_event(row) if row else None


async def get_user_events_upcoming(
    conn: DbConn,
    user_id: int,
    from_dt: datetime,
    to_dt: datetime,
    include_completed: bool = False,
) -> list[Event]:
    """Get user events in date range (active only: not cancelled)."""
    extra = "" if include_completed else " AND is_completed = 0"
    from_val = from_dt.isoformat() if isinstance(from_dt, datetime) else from_dt
    to_val = to_dt.isoformat() if isinstance(to_dt, datetime) else to_dt
    rows = await conn.fetchall(
        f"""SELECT {_EVENT_SELECT}
            FROM events
            WHERE user_id = ? AND event_datetime >= ? AND event_datetime <= ?
              AND is_cancelled = 0{extra}
            ORDER BY event_datetime ASC""",
        (user_id, from_val, to_val),
    )
    return [_row_to_event(r) for r in rows]


async def get_events_to_notify(conn: DbConn, now: datetime = None) -> list[tuple[int, int, Event]]:
    """First notification: event time in window, never notified, not cancelled/completed."""
    now = now or utc_now()
    window_start = (now - timedelta(minutes=2)).isoformat()
    window_end = now.isoformat()

    rows = await conn.fetchall(
        f"""SELECT {_EVENT_SELECT_E}, u.telegram_id
           FROM events e
           JOIN users u ON e.user_id = u.id
           WHERE e.is_completed = 0 AND e.is_cancelled = 0
             AND e.notified_at IS NULL AND e.nudge_count = 0
             AND e.event_datetime >= ? AND e.event_datetime <= ?""",
        (window_start, window_end),
    )
    result = []
    for r in rows:
        event = _row_to_event(r[:15])
        result.append((r[15], r[1], event))
    return result


async def get_events_to_nudge(
    conn: DbConn,
    now: datetime = None,
    interval_minutes: int = 30,
) -> list[tuple[int, int, Event]]:
    """2nd and 3rd reminders: nudge_count 1 or 2, last notify >= interval ago, max 3 total sends."""
    now = now or utc_now()
    threshold = (now - timedelta(minutes=interval_minutes)).isoformat()

    rows = await conn.fetchall(
        f"""SELECT {_EVENT_SELECT_E}, u.telegram_id
           FROM events e
           JOIN users u ON e.user_id = u.id
           WHERE e.is_completed = 0 AND e.is_cancelled = 0
             AND e.notified_at IS NOT NULL
             AND e.nudge_count >= 1 AND e.nudge_count < 3
             AND e.notified_at <= ?""",
        (threshold,),
    )
    result = []
    for r in rows:
        event = _row_to_event(r[:15])
        result.append((r[15], r[1], event))
    return result


async def advance_recurring_event(conn: DbConn, event: Event) -> bool:
    """For recurring events, update event_datetime to next occurrence."""
    import calendar

    if event.recurrence_type == RECURRENCE_NONE:
        return False

    dt = event.event_datetime

    if event.recurrence_type == RECURRENCE_MONTHLY and event.recurrence_value:
        day = int(event.recurrence_value)
        try:
            next_month = dt.month + 1
            next_year = dt.year
            if next_month > 12:
                next_month = 1
                next_year += 1
            max_day = calendar.monthrange(next_year, next_month)[1]
            safe_day = min(day, max_day)
            new_dt = dt.replace(year=next_year, month=next_month, day=safe_day)
        except (ValueError, TypeError):
            new_dt = dt + timedelta(days=28)
    elif event.recurrence_type == RECURRENCE_WEEKLY and event.recurrence_value:
        target_weekday = int(event.recurrence_value)
        days_ahead = (target_weekday - dt.weekday() + 7) % 7
        if days_ahead == 0:
            days_ahead = 7
        new_dt = dt + timedelta(days=days_ahead)
    else:
        return False

    await conn.execute(
        "UPDATE events SET event_datetime = ?, notified_at = NULL, nudge_count = 0 WHERE id = ?",
        (new_dt.isoformat(), event.id),
    )
    return True


async def mark_notified(conn: DbConn, event_id: int, at: datetime) -> None:
    """After first notification: notified_at + nudge_count = 1."""
    await conn.execute(
        "UPDATE events SET notified_at = ?, nudge_count = 1 WHERE id = ?",
        (at.isoformat(), event_id),
    )


async def record_nudge_sent(conn: DbConn, event_id: int, at: datetime) -> None:
    """Increment nudge_count and refresh notified_at (2nd/3rd reminder)."""
    await conn.execute(
        "UPDATE events SET notified_at = ?, nudge_count = nudge_count + 1 WHERE id = ? AND nudge_count < 3",
        (at.isoformat(), event_id),
    )


async def mark_completed(conn: DbConn, event_id: int) -> bool:
    """Mark event as completed."""
    at = utc_now().isoformat()
    n = await conn.execute_rowcount(
        "UPDATE events SET is_completed = 1, completed_at = ?, nudge_count = 0, notified_at = NULL WHERE id = ?",
        (at, event_id),
    )
    return n > 0


async def mark_cancelled(conn: DbConn, event_id: int) -> bool:
    """Soft cancel (keeps row for history)."""
    at = utc_now().isoformat()
    n = await conn.execute_rowcount(
        "UPDATE events SET is_cancelled = 1, cancelled_at = ?, nudge_count = 0, notified_at = NULL WHERE id = ?",
        (at, event_id),
    )
    return n > 0


async def postpone_event(conn: DbConn, event_id: int, hours: int = 1) -> bool:
    """Postpone event by N hours. Clears notification state for next cycle."""
    row = await conn.fetchone("SELECT event_datetime FROM events WHERE id = ?", (event_id,))
    if not row:
        return False
    old_dt = datetime.fromisoformat(row[0]) if isinstance(row[0], str) else row[0]
    new_dt = old_dt + timedelta(hours=hours)
    await conn.execute(
        "UPDATE events SET event_datetime = ?, notified_at = NULL, nudge_count = 0 WHERE id = ?",
        (new_dt.isoformat(), event_id),
    )
    return True


async def update_event(
    conn: DbConn,
    event_id: int,
    *,
    title: Optional[str] = None,
    description: Optional[str] = None,
    event_datetime: Optional[datetime] = None,  # Must be UTC when updating
    timezone: Optional[str] = None,
    recurrence_type: Optional[str] = None,
    recurrence_value: Optional[str] = None,
) -> bool:
    """Update event fields."""
    updates = []
    params = []
    if title is not None:
        updates.append("title = ?")
        params.append(title)
    if description is not None:
        updates.append("description = ?")
        params.append(description)
    if event_datetime is not None:
        updates.append("event_datetime = ?")
        params.append(event_datetime.isoformat())
    if timezone is not None:
        updates.append("timezone = ?")
        params.append(timezone)
    if recurrence_type is not None:
        updates.append("recurrence_type = ?")
        params.append(recurrence_type)
    if recurrence_value is not None:
        updates.append("recurrence_value = ?")
        params.append(recurrence_value)
    if not updates:
        return False
    params.append(event_id)
    n = await conn.execute_rowcount(
        f"UPDATE events SET {', '.join(updates)} WHERE id = ?",
        tuple(params),
    )
    return n > 0


async def delete_event(conn: DbConn, event_id: int) -> bool:
    """Delete event."""
    n = await conn.execute_rowcount("DELETE FROM events WHERE id = ?", (event_id,))
    return n > 0


async def get_events_by_user_id(conn: DbConn, user_db_id: int) -> list[Event]:
    """Get all active non-completed events for user."""
    rows = await conn.fetchall(
        f"""SELECT {_EVENT_SELECT}
           FROM events WHERE user_id = ? AND is_completed = 0 AND is_cancelled = 0
           ORDER BY event_datetime ASC""",
        (user_db_id,),
    )
    return [_row_to_event(r) for r in rows]


async def get_user_events_completed(
    conn: DbConn,
    user_id: int,
    limit: int = 50,
) -> list[Event]:
    """Completed events, newest first."""
    rows = await conn.fetchall(
        f"""SELECT {_EVENT_SELECT}
           FROM events
           WHERE user_id = ? AND is_completed = 1 AND is_cancelled = 0
           ORDER BY COALESCE(completed_at, created_at) DESC
           LIMIT ?""",
        (user_id, limit),
    )
    return [_row_to_event(r) for r in rows]


async def get_user_events_cancelled(
    conn: DbConn,
    user_id: int,
    limit: int = 50,
) -> list[Event]:
    """Cancelled events, newest first."""
    rows = await conn.fetchall(
        f"""SELECT {_EVENT_SELECT}
           FROM events
           WHERE user_id = ? AND is_cancelled = 1
           ORDER BY COALESCE(cancelled_at, created_at) DESC
           LIMIT ?""",
        (user_id, limit),
    )
    return [_row_to_event(r) for r in rows]


async def update_user_language(conn: DbConn, telegram_id: int, lang: str) -> None:
    """Update user language."""
    await conn.execute("UPDATE users SET language = ? WHERE telegram_id = ?", (lang, telegram_id))


async def update_user_timezone(conn: DbConn, telegram_id: int, tz: str) -> None:
    """Update user timezone."""
    await conn.execute("UPDATE users SET timezone = ? WHERE telegram_id = ?", (tz, telegram_id))


async def get_user_settings(conn: DbConn, telegram_id: int) -> Optional[tuple[str, str]]:
    """Get (language, timezone) for user."""
    row = await conn.fetchone("SELECT language, timezone FROM users WHERE telegram_id = ?", (telegram_id,))
    return row if row else None
