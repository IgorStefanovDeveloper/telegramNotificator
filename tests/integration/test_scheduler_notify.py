"""Integration: scheduler notification side effects on DB (mocked Telegram)."""
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

pytestmark = pytest.mark.integration

from config import DEFAULT_TIMEZONE
from database.db import get_db
from database.events_repo import get_or_create_user, create_event, get_event_by_id
from database.models import RECURRENCE_WEEKLY
from utils_timezone import local_to_utc


@pytest.mark.asyncio
async def test_scheduler_one_shot_marks_notified(clean_db, monkeypatch):
    conn = await get_db()
    try:
        uid = await get_or_create_user(conn, 70001)
        now_local = datetime(2026, 1, 10, 14, 30)
        eid = await create_event(conn, user_id=uid, title="Sched test", event_datetime=now_local)
    finally:
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
async def test_scheduler_recurring_advances_no_stale_notify(clean_db, monkeypatch):
    conn = await get_db()
    try:
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
    finally:
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
