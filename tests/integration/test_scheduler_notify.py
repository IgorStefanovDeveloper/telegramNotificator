"""Integration: scheduler notification side effects on DB (mocked Telegram)."""
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import aiosqlite
import pytest

pytestmark = pytest.mark.integration

from config import DEFAULT_TIMEZONE
from database.connection import SqliteDbConn
from database.db import init_schema
from database.events_repo import get_or_create_user, create_event, get_event_by_id
from database.models import RECURRENCE_WEEKLY
from utils_timezone import local_to_utc


def _make_get_db(path):
    async def _get_db():
        raw = await aiosqlite.connect(path)
        return SqliteDbConn(raw)

    return _get_db


@pytest.mark.asyncio
async def test_scheduler_one_shot_marks_notified(tmp_path, monkeypatch):
    db_path = tmp_path / "sched.db"
    get_db = _make_get_db(db_path)
    monkeypatch.setattr("database.db.get_db", get_db)
    monkeypatch.setattr("scheduler.get_db", get_db)

    conn = await get_db()
    await init_schema(conn)
    uid = await get_or_create_user(conn, 70001)
    now_local = datetime(2026, 1, 10, 14, 30)
    eid = await create_event(conn, user_id=uid, title="Sched test", event_datetime=now_local)
    await conn.close()

    now_utc = local_to_utc(now_local, DEFAULT_TIMEZONE)
    monkeypatch.setattr("utils_timezone.utc_now", lambda: now_utc)

    from scheduler import send_notifications

    bot = MagicMock()
    bot.send_message = AsyncMock()
    await send_notifications(bot)

    bot.send_message.assert_called_once()
    conn = await get_db()
    try:
        ev = await get_event_by_id(conn, eid)
        assert ev.notified_at is not None
        assert ev.nudge_count == 1
    finally:
        await conn.close()


@pytest.mark.asyncio
async def test_scheduler_recurring_advances_no_stale_notify(tmp_path, monkeypatch):
    db_path = tmp_path / "sched2.db"
    get_db = _make_get_db(db_path)
    monkeypatch.setattr("database.db.get_db", get_db)
    monkeypatch.setattr("scheduler.get_db", get_db)

    conn = await get_db()
    await init_schema(conn)
    uid = await get_or_create_user(conn, 70002)
    now_local = datetime(2026, 2, 2, 10, 0)
    eid = await create_event(
        conn,
        user_id=uid,
        title="Weekly sched",
        event_datetime=now_local,
        recurrence_type=RECURRENCE_WEEKLY,
        recurrence_value="0",
    )
    await conn.close()

    now_utc = local_to_utc(now_local, DEFAULT_TIMEZONE)
    monkeypatch.setattr("utils_timezone.utc_now", lambda: now_utc)

    from scheduler import send_notifications

    bot = MagicMock()
    bot.send_message = AsyncMock()
    await send_notifications(bot)

    conn = await get_db()
    try:
        ev = await get_event_by_id(conn, eid)
        assert ev.notified_at is None
        assert ev.nudge_count == 0
        assert ev.event_datetime > now_utc
    finally:
        await conn.close()
