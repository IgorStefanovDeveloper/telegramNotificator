"""Pytest fixtures: PostgreSQL only."""
import os

# Must run before importing config / database (dotenv does not override existing env).
if os.getenv("TEST_DATABASE_URL"):
    os.environ["DATABASE_URL"] = os.environ["TEST_DATABASE_URL"]

if not os.getenv("DATABASE_URL"):
    # Local default: docker run -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=telegram_bot_test postgres:16
    os.environ["DATABASE_URL"] = (
        "postgresql://postgres:postgres@127.0.0.1:5432/telegram_bot_test"
    )
    os.environ.setdefault("DATABASE_SSL", "0")

import pytest

_schema_ready = False


async def _ensure_schema() -> None:
    global _schema_ready
    from database.db import init_schema_postgres

    if not _schema_ready:
        await init_schema_postgres()
        _schema_ready = True


async def _truncate() -> None:
    from database.db import get_db

    conn = await get_db()
    try:
        await conn.execute("TRUNCATE TABLE events, users RESTART IDENTITY CASCADE")
    finally:
        await conn.close()


@pytest.fixture
async def db_conn():
    """PostgreSQL connection; users/events truncated before each test."""
    await _ensure_schema()
    await _truncate()
    from database.db import get_db

    conn = await get_db()
    try:
        yield conn
    finally:
        await conn.close()


@pytest.fixture
async def clean_db():
    """Empty users/events; use with tests that call real get_db() (handlers, scheduler)."""
    await _ensure_schema()
    await _truncate()
    yield
