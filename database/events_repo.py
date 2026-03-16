"""Event repository - CRUD and queries."""
from datetime import datetime, timedelta
from typing import Optional

import aiosqlite

from config import DEFAULT_TIMEZONE, MAX_FUTURE_MONTHS
from database.models import Event, RECURRENCE_NONE, RECURRENCE_MONTHLY, RECURRENCE_WEEKLY


def _row_to_event(row: tuple) -> Event:
    return Event(
        id=row[0],
        user_id=row[1],
        title=row[2],
        description=row[3],
        event_datetime=datetime.fromisoformat(row[4]) if row[4] else None,
        timezone=row[5] or DEFAULT_TIMEZONE,
        recurrence_type=row[6] or RECURRENCE_NONE,
        recurrence_value=row[7],
        is_completed=bool(row[8]),
        created_at=datetime.fromisoformat(row[9]) if row[9] else datetime.now(),
    )


async def get_or_create_user(conn: aiosqlite.Connection, telegram_id: int) -> int:
    """Get user id by telegram_id, create if not exists. Returns user.id (pk)."""
    cursor = await conn.execute(
        "SELECT id FROM users WHERE telegram_id = ?", (telegram_id,)
    )
    row = await cursor.fetchone()
    if row:
        return row[0]
    await conn.execute(
        "INSERT INTO users (telegram_id, language, timezone) VALUES (?, 'ru', ?)",
        (telegram_id, DEFAULT_TIMEZONE),
    )
    await conn.commit()
    cursor = await conn.execute("SELECT id FROM users WHERE telegram_id = ?", (telegram_id,))
    row = await cursor.fetchone()
    return row[0]


async def create_event(
    conn: aiosqlite.Connection,
    user_id: int,
    title: str,
    event_datetime: datetime,
    timezone: str = DEFAULT_TIMEZONE,
    description: Optional[str] = None,
    recurrence_type: str = RECURRENCE_NONE,
    recurrence_value: Optional[str] = None,
) -> int:
    """Create event and return its id."""
    cursor = await conn.execute(
        """INSERT INTO events (user_id, title, description, event_datetime, timezone, recurrence_type, recurrence_value)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            user_id,
            title,
            description or "",
            event_datetime.isoformat(),
            timezone,
            recurrence_type,
            recurrence_value or "",
        ),
    )
    await conn.commit()
    return cursor.lastrowid


async def get_event_by_id(conn: aiosqlite.Connection, event_id: int) -> Optional[Event]:
    """Get event by id."""
    cursor = await conn.execute(
        "SELECT id, user_id, title, description, event_datetime, timezone, recurrence_type, recurrence_value, is_completed, created_at FROM events WHERE id = ?",
        (event_id,),
    )
    row = await cursor.fetchone()
    return _row_to_event(row) if row else None


async def get_user_events_upcoming(
    conn: aiosqlite.Connection,
    user_id: int,
    from_dt: datetime,
    to_dt: datetime,
    include_completed: bool = False,
) -> list[Event]:
    """Get user events in date range."""
    extra = "" if include_completed else " AND is_completed = 0"
    cursor = await conn.execute(
        f"""SELECT id, user_id, title, description, event_datetime, timezone, recurrence_type, recurrence_value, is_completed, created_at
            FROM events
            WHERE user_id = ? AND event_datetime >= ? AND event_datetime <= ?{extra}
            ORDER BY event_datetime ASC""",
        (user_id, from_dt.isoformat(), to_dt.isoformat()),
    )
    rows = await cursor.fetchall()
    return [_row_to_event(r) for r in rows]


async def get_events_to_notify(conn: aiosqlite.Connection, now: datetime) -> list[tuple[int, int, Event]]:
    """Get events that should be notified now. Returns list of (telegram_id, user_db_id, event)."""
    window_start = (now - timedelta(minutes=2)).isoformat()
    window_end = now.isoformat()

    cursor = await conn.execute(
        """SELECT e.id, e.user_id, e.title, e.description, e.event_datetime, e.timezone, e.recurrence_type, e.recurrence_value, e.is_completed, e.created_at, u.telegram_id
           FROM events e
           JOIN users u ON e.user_id = u.id
           WHERE e.is_completed = 0 AND e.notified_at IS NULL
             AND e.event_datetime >= ? AND e.event_datetime <= ?""",
        (window_start, window_end),
    )
    rows = await cursor.fetchall()
    result = []
    for r in rows:
        event = _row_to_event(r[:10])
        result.append((r[10], r[1], event))
    return result


async def advance_recurring_event(conn: aiosqlite.Connection, event: Event) -> bool:
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
        "UPDATE events SET event_datetime = ?, notified_at = NULL WHERE id = ?",
        (new_dt.isoformat(), event.id),
    )
    await conn.commit()
    return True


async def mark_notified(conn: aiosqlite.Connection, event_id: int, at: datetime) -> None:
    """Mark event as notified to avoid duplicate notifications."""
    await conn.execute(
        "UPDATE events SET notified_at = ? WHERE id = ?",
        (at.isoformat(), event_id),
    )
    await conn.commit()


async def mark_completed(conn: aiosqlite.Connection, event_id: int) -> bool:
    """Mark event as completed."""
    cursor = await conn.execute(
        "UPDATE events SET is_completed = 1 WHERE id = ?", (event_id,)
    )
    await conn.commit()
    return cursor.rowcount > 0


async def postpone_event(conn: aiosqlite.Connection, event_id: int, hours: int = 1) -> bool:
    """Postpone event by N hours. Clears notified_at so it can be notified again."""
    cursor = await conn.execute("SELECT event_datetime FROM events WHERE id = ?", (event_id,))
    row = await cursor.fetchone()
    if not row:
        return False
    old_dt = datetime.fromisoformat(row[0])
    new_dt = old_dt + timedelta(hours=hours)
    await conn.execute(
        "UPDATE events SET event_datetime = ?, notified_at = NULL WHERE id = ?",
        (new_dt.isoformat(), event_id),
    )
    await conn.commit()
    return True


async def update_event(
    conn: aiosqlite.Connection,
    event_id: int,
    *,
    title: Optional[str] = None,
    description: Optional[str] = None,
    event_datetime: Optional[datetime] = None,
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
    await conn.execute(
        f"UPDATE events SET {', '.join(updates)} WHERE id = ?", params
    )
    await conn.commit()
    return True


async def delete_event(conn: aiosqlite.Connection, event_id: int) -> bool:
    """Delete event."""
    cursor = await conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
    await conn.commit()
    return cursor.rowcount > 0


async def get_events_by_user_id(conn: aiosqlite.Connection, user_db_id: int) -> list[Event]:
    """Get all non-completed events for user."""
    cursor = await conn.execute(
        """SELECT id, user_id, title, description, event_datetime, timezone, recurrence_type, recurrence_value, is_completed, created_at
           FROM events WHERE user_id = ? AND is_completed = 0 ORDER BY event_datetime ASC""",
        (user_db_id,),
    )
    rows = await cursor.fetchall()
    return [_row_to_event(r) for r in rows]


async def update_user_language(conn: aiosqlite.Connection, telegram_id: int, lang: str) -> None:
    """Update user language."""
    await conn.execute("UPDATE users SET language = ? WHERE telegram_id = ?", (lang, telegram_id))
    await conn.commit()


async def update_user_timezone(conn: aiosqlite.Connection, telegram_id: int, tz: str) -> None:
    """Update user timezone."""
    await conn.execute("UPDATE users SET timezone = ? WHERE telegram_id = ?", (tz, telegram_id))
    await conn.commit()


async def get_user_settings(conn: aiosqlite.Connection, telegram_id: int) -> Optional[tuple[str, str]]:
    """Get (language, timezone) for user."""
    cursor = await conn.execute(
        "SELECT language, timezone FROM users WHERE telegram_id = ?", (telegram_id,)
    )
    row = await cursor.fetchone()
    return row if row else None
