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
    get_events_to_nudge,
    record_nudge_sent,
    mark_cancelled,
    get_user_events_completed,
    get_user_events_cancelled,
    get_user_events_upcoming,
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


@pytest.mark.asyncio
async def test_mark_notified_sets_nudge_count(db_conn):
    user_id = await get_or_create_user(db_conn, 556)
    eid = await create_event(db_conn, user_id=user_id, title="N", event_datetime=datetime(2025, 11, 21, 10, 0))
    now = local_to_utc(datetime(2025, 11, 21, 10, 0), DEFAULT_TIMEZONE)
    await mark_notified(db_conn, eid, now)
    ev = await get_event_by_id(db_conn, eid)
    assert ev.nudge_count == 1
    assert ev.notified_at is not None


@pytest.mark.asyncio
async def test_get_events_to_nudge_and_record_nudge(db_conn):
    user_id = await get_or_create_user(db_conn, 557)
    eid = await create_event(db_conn, user_id=user_id, title="Nudge me", event_datetime=datetime(2025, 11, 22, 12, 0))
    t0 = local_to_utc(datetime(2025, 11, 22, 12, 0), DEFAULT_TIMEZONE)
    await mark_notified(db_conn, eid, t0)
    # Too soon: no nudge
    assert len(await get_events_to_nudge(db_conn, t0)) == 0
    t_later = t0 + timedelta(minutes=31)
    nudges = await get_events_to_nudge(db_conn, t_later)
    assert len(nudges) == 1
    await record_nudge_sent(db_conn, eid, t_later)
    ev = await get_event_by_id(db_conn, eid)
    assert ev.nudge_count == 2


@pytest.mark.asyncio
async def test_mark_cancelled_and_lists(db_conn):
    user_id = await get_or_create_user(db_conn, 558)
    eid = await create_event(db_conn, user_id=user_id, title="Cancel me", event_datetime=datetime(2025, 12, 5, 15, 0))
    await mark_cancelled(db_conn, eid)
    ev = await get_event_by_id(db_conn, eid)
    assert ev.is_cancelled is True
    now = local_to_utc(datetime(2025, 12, 1, 0, 0), DEFAULT_TIMEZONE)
    to_dt = local_to_utc(datetime(2026, 12, 31, 0, 0), DEFAULT_TIMEZONE)
    upcoming = await get_user_events_upcoming(db_conn, user_id, now, to_dt)
    assert all(e.id != eid for e in upcoming)
    cancelled = await get_user_events_cancelled(db_conn, user_id)
    assert len(cancelled) == 1
    assert cancelled[0].title == "Cancel me"


@pytest.mark.asyncio
async def test_mark_completed_list(db_conn):
    user_id = await get_or_create_user(db_conn, 559)
    eid = await create_event(db_conn, user_id=user_id, title="Done me", event_datetime=datetime(2025, 12, 6, 16, 0))
    await mark_completed(db_conn, eid)
    ev = await get_event_by_id(db_conn, eid)
    assert ev.is_completed is True
    assert ev.completed_at is not None
    done_list = await get_user_events_completed(db_conn, user_id)
    assert len(done_list) == 1
    assert done_list[0].title == "Done me"


@pytest.mark.asyncio
async def test_nudge_stops_at_three(db_conn):
    user_id = await get_or_create_user(db_conn, 561)
    eid = await create_event(db_conn, user_id=user_id, title="Three max", event_datetime=datetime(2025, 11, 25, 8, 0))
    t0 = local_to_utc(datetime(2025, 11, 25, 8, 0), DEFAULT_TIMEZONE)
    await mark_notified(db_conn, eid, t0)
    t1 = t0 + timedelta(minutes=31)
    await record_nudge_sent(db_conn, eid, t1)
    t2 = t1 + timedelta(minutes=31)
    await record_nudge_sent(db_conn, eid, t2)
    ev = await get_event_by_id(db_conn, eid)
    assert ev.nudge_count == 3
    assert len(await get_events_to_nudge(db_conn, t2 + timedelta(minutes=31))) == 0


@pytest.mark.asyncio
async def test_advance_recurring_resets_nudge(db_conn):
    user_id = await get_or_create_user(db_conn, 560)
    eid = await create_event(
        db_conn,
        user_id=user_id,
        title="W",
        event_datetime=datetime(2025, 10, 13, 9, 0),
        recurrence_type=RECURRENCE_WEEKLY,
        recurrence_value="0",
    )
    await mark_notified(db_conn, eid, local_to_utc(datetime(2025, 10, 13, 9, 0), DEFAULT_TIMEZONE))
    event = await get_event_by_id(db_conn, eid)
    await advance_recurring_event(db_conn, event)
    event = await get_event_by_id(db_conn, eid)
    assert event.nudge_count == 0
    assert event.notified_at is None
