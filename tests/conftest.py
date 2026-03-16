"""Pytest fixtures for in-memory database."""
import pytest
import aiosqlite

from database.db import init_schema


@pytest.fixture
async def db_conn():
    """Fresh in-memory SQLite connection with schema."""
    conn = await aiosqlite.connect(":memory:")
    await init_schema(conn)
    yield conn
    await conn.close()
