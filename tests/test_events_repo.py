"""Tests for events repository."""
from datetime import datetime, timedelta

import pytest

from config import DEFAULT_TIMEZONE
from utils_timezone import local_to_utc
from database.events_repo import (
    get_or_create_user,
    create_event,
    get_event_by_id,
    update_event,
    mark_completed,
    postpone_event,
    advance_recurring_event,
    mark_notified,
    get_events_to_notify,
)
from database.models import RECURRENCE_NONE, RECURRENCE_MONTHLY, RECURRENCE_WEEKLY


@pytest.mark.asyncio
async def test_create_event(db_conn):
    user_id = await get_or_create_user(db_conn, 12345)
    event_id = await create_event(
        db_conn,
        user_id=user_id,
        title="Test event",
        event_datetime=datetime(2025, 5, 19, 14, 30),
    )
    assert event_id is not None
    event = await get_event_by_id(db_conn, event_id)
    assert event is not None
    assert event.title == "Test event"
    assert event.recurrence_type == RECURRENCE_NONE


@pytest.mark.asyncio
async def test_update_event(db_conn):
    user_id = await get_or_create_user(db_conn, 999)
    event_id = await create_event(
        db_conn,
        user_id=user_id,
        title="Old title",
        event_datetime=datetime(2025, 6, 1, 10, 0),
    )
    ok = await update_event(db_conn, event_id, title="New title")
    assert ok is True
    event = await get_event_by_id(db_conn, event_id)
    assert event.title == "New title"


@pytest.mark.asyncio
async def test_update_event_datetime_utc(db_conn):
    """update_event with event_datetime must accept UTC (used when editing)."""
    user_id = await get_or_create_user(db_conn, 888)
    dt_local = datetime(2025, 8, 10, 15, 0)
    event_id = await create_event(
        db_conn,
        user_id=user_id,
        title="Edit datetime",
        event_datetime=dt_local,
    )
    # 20:30 Moscow = 17:30 UTC
    new_dt_utc = local_to_utc(datetime(2025, 8, 15, 20, 30), DEFAULT_TIMEZONE)
    ok = await update_event(db_conn, event_id, event_datetime=new_dt_utc)
    assert ok is True
    event = await get_event_by_id(db_conn, event_id)
    assert event.event_datetime == new_dt_utc
    assert event.event_datetime.day == 15


@pytest.mark.asyncio
async def test_postpone_event(db_conn):
    user_id = await get_or_create_user(db_conn, 111)
    dt_local = datetime(2025, 7, 15, 12, 0)
    event_id = await create_event(db_conn, user_id=user_id, title="Postpone me", event_datetime=dt_local)
    ok = await postpone_event(db_conn, event_id, hours=1)
    assert ok is True
    event = await get_event_by_id(db_conn, event_id)
    expected_utc = local_to_utc(dt_local + timedelta(hours=1), DEFAULT_TIMEZONE)
    assert event.event_datetime == expected_utc


@pytest.mark.asyncio
async def test_mark_completed(db_conn):
    user_id = await get_or_create_user(db_conn, 222)
    event_id = await create_event(db_conn, user_id=user_id, title="Complete me", event_datetime=datetime(2025, 8, 1, 9, 0))
    ok = await mark_completed(db_conn, event_id)
    assert ok is True
    event = await get_event_by_id(db_conn, event_id)
    assert event.is_completed is True


@pytest.mark.asyncio
async def test_advance_recurring_monthly(db_conn):
    user_id = await get_or_create_user(db_conn, 333)
    dt = datetime(2025, 9, 19, 10, 0)
    event_id = await create_event(
        db_conn,
        user_id=user_id,
        title="Monthly",
        event_datetime=dt,
        recurrence_type=RECURRENCE_MONTHLY,
        recurrence_value="19",
    )
    event = await get_event_by_id(db_conn, event_id)
    ok = await advance_recurring_event(db_conn, event)
    assert ok is True
    event = await get_event_by_id(db_conn, event_id)
    assert event.event_datetime.month == 10
    assert event.event_datetime.day == 19


@pytest.mark.asyncio
async def test_advance_recurring_weekly(db_conn):
    user_id = await get_or_create_user(db_conn, 444)
    dt_local = datetime(2025, 10, 13, 9, 0)  # Monday
    event_id = await create_event(
        db_conn,
        user_id=user_id,
        title="Weekly",
        event_datetime=dt_local,
        recurrence_type=RECURRENCE_WEEKLY,
        recurrence_value="0",  # Monday
    )
    event = await get_event_by_id(db_conn, event_id)
    stored_utc = event.event_datetime
    ok = await advance_recurring_event(db_conn, event)
    assert ok is True
    event = await get_event_by_id(db_conn, event_id)
    assert event.event_datetime.weekday() == 0
    assert (event.event_datetime - stored_utc).days == 7


@pytest.mark.asyncio
async def test_get_events_to_notify(db_conn):
    user_id = await get_or_create_user(db_conn, 555)
    now_local = datetime(2025, 11, 20, 14, 30)
    event_id = await create_event(db_conn, user_id=user_id, title="Due now", event_datetime=now_local)
    now_utc = local_to_utc(now_local, DEFAULT_TIMEZONE)
    events = await get_events_to_notify(db_conn, now_utc)
    assert len(events) == 1
    assert events[0][2].id == event_id
    assert events[0][2].title == "Due now"

    await mark_notified(db_conn, event_id, now_utc)
    events2 = await get_events_to_notify(db_conn, now_utc)
    assert len(events2) == 0
