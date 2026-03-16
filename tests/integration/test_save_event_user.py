"""
Integration tests for _save_event user attribution.

Covers the bug: when _save_event is called from a CallbackQuery handler,
cb.message.from_user is the BOT, not the user. Events must be saved under
cb.from_user.id (the actual user who pressed the button).
"""
import pytest

pytestmark = pytest.mark.integration
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from database.db import init_schema
from database.events_repo import get_user_events_upcoming, get_or_create_user


BOT_TELEGRAM_ID = 999999
USER_TELEGRAM_ID = 12345


@pytest.fixture
def temp_db_path(tmp_path):
    """Temp directory for DB file. Patches config before init_db."""
    db_path = tmp_path / "events.db"
    return db_path


@pytest.fixture
async def integration_db(temp_db_path, monkeypatch):
    """DB in temp path with schema, for integration tests."""
    monkeypatch.setattr("handlers.events.get_db", _make_get_db(temp_db_path))
    conn = await _connect(temp_db_path)
    await init_schema(conn)
    await conn.close()
    yield temp_db_path


def _make_get_db(path: Path):
    """Factory for get_db that connects to path."""

    async def _get_db():
        return await _connect(path)

    return _get_db


async def _connect(path: Path):
    import aiosqlite
    path.parent.mkdir(parents=True, exist_ok=True)
    return await aiosqlite.connect(path)


@pytest.fixture
def mock_state():
    """Mock FSMContext with event data."""
    state = Mock()
    state.get_data = AsyncMock(
        return_value={
            "title": "Integration Test Event",
            "event_datetime": datetime(2025, 12, 1, 14, 0),
            "timezone": "Europe/Moscow",
            "lang": "ru",
        }
    )
    state.clear = AsyncMock()
    return state


@pytest.fixture
def mock_message_from_bot():
    """Simulates cb.message - the message with inline keyboard sent by the BOT."""
    msg = Mock()
    msg.from_user = Mock()
    msg.from_user.id = BOT_TELEGRAM_ID
    msg.edit_text = AsyncMock()
    return msg


@pytest.fixture
def mock_message_from_user():
    """Simulates message from the user (e.g. typed day of month)."""
    msg = Mock()
    msg.from_user = Mock()
    msg.from_user.id = USER_TELEGRAM_ID
    msg.answer = AsyncMock()
    del msg.edit_text  # User's Message has no edit_text; use answer path
    return msg


@pytest.mark.asyncio
async def test_save_event_from_callback_saves_to_correct_user(
    integration_db, mock_state, mock_message_from_bot, monkeypatch
):
    """
    When _save_event is called from a callback (message.from_user = bot),
    passing telegram_id explicitly must save the event under that user.
    """
    monkeypatch.setattr("handlers.events.get_db", _make_get_db(integration_db))

    from handlers.events import _save_event

    await _save_event(
        mock_message_from_bot,
        mock_state,
        "none",
        None,
        telegram_id=USER_TELEGRAM_ID,
    )

    conn = await _connect(integration_db)
    try:
        user_db_id = await get_or_create_user(conn, USER_TELEGRAM_ID)
        from_dt = datetime(2025, 1, 1)
        to_dt = datetime(2026, 12, 31)
        events = await get_user_events_upcoming(conn, user_db_id, from_dt, to_dt)
        assert len(events) == 1
        assert events[0].title == "Integration Test Event"
    finally:
        await conn.close()


@pytest.mark.asyncio
async def test_save_event_from_callback_without_telegram_id_saves_to_wrong_user(
    integration_db, mock_state, mock_message_from_bot, monkeypatch
):
    """
    Regression: WITHOUT telegram_id, event would be saved under message.from_user (bot).
    The user's list would be empty.
    """
    monkeypatch.setattr("handlers.events.get_db", _make_get_db(integration_db))

    from handlers.events import _save_event

    await _save_event(mock_message_from_bot, mock_state, "none", None)
    # No telegram_id passed - uses message.from_user.id = BOT_TELEGRAM_ID

    conn = await _connect(integration_db)
    try:
        user_db_id = await get_or_create_user(conn, USER_TELEGRAM_ID)
        from_dt = datetime(2025, 1, 1)
        to_dt = datetime(2026, 12, 31)
        events = await get_user_events_upcoming(conn, user_db_id, from_dt, to_dt)
        assert len(events) == 0, (
            "Bug: event saved under user's ID when it should be under bot's. "
            "When called from callback without telegram_id, event goes to message.from_user (bot)."
        )

        bot_user_id = await get_or_create_user(conn, BOT_TELEGRAM_ID)
        bot_events = await get_user_events_upcoming(conn, bot_user_id, from_dt, to_dt)
        assert len(bot_events) == 1, "Event should be under bot's user when telegram_id not passed"
    finally:
        await conn.close()


@pytest.mark.asyncio
async def test_save_event_from_message_saves_to_correct_user(
    integration_db, mock_state, mock_message_from_user, monkeypatch
):
    """
    When _save_event is called from a Message (user typed text), no telegram_id needed.
    message.from_user.id is the actual user.
    """
    monkeypatch.setattr("handlers.events.get_db", _make_get_db(integration_db))

    from handlers.events import _save_event

    await _save_event(mock_message_from_user, mock_state, "monthly", "19")
    # No telegram_id - uses message.from_user.id = USER_TELEGRAM_ID

    conn = await _connect(integration_db)
    try:
        user_db_id = await get_or_create_user(conn, USER_TELEGRAM_ID)
        from_dt = datetime(2025, 1, 1)
        to_dt = datetime(2026, 12, 31)
        events = await get_user_events_upcoming(conn, user_db_id, from_dt, to_dt)
        assert len(events) == 1
        assert events[0].recurrence_type == "monthly"
        assert events[0].recurrence_value == "19"
    finally:
        await conn.close()


@pytest.mark.asyncio
async def test_save_event_weekly_from_callback_saves_to_correct_user(
    integration_db, mock_state, mock_message_from_bot, monkeypatch
):
    """
    Weekly recurring event from callback (day of week) — must save under telegram_id.
    """
    monkeypatch.setattr("handlers.events.get_db", _make_get_db(integration_db))

    from handlers.events import _save_event

    await _save_event(
        mock_message_from_bot,
        mock_state,
        "weekly",
        "0",  # Monday
        telegram_id=USER_TELEGRAM_ID,
    )

    conn = await _connect(integration_db)
    try:
        user_db_id = await get_or_create_user(conn, USER_TELEGRAM_ID)
        from_dt = datetime(2025, 1, 1)
        to_dt = datetime(2026, 12, 31)
        events = await get_user_events_upcoming(conn, user_db_id, from_dt, to_dt)
        assert len(events) == 1
        assert events[0].recurrence_type == "weekly"
        assert events[0].recurrence_value == "0"
    finally:
        await conn.close()
