"""Pytest fixtures for in-memory database."""
import pytest
import aiosqlite

from database.connection import SqliteDbConn
from database.db import init_sqlite_schema_raw


@pytest.fixture
async def db_conn():
    """Fresh in-memory SQLite with schema (same API as production DB layer)."""
    raw = await aiosqlite.connect(":memory:")
    await init_sqlite_schema_raw(raw)
    try:
        yield SqliteDbConn(raw)
    finally:
        await raw.close()
