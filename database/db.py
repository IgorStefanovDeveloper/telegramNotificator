"""Database: PostgreSQL only (asyncpg pool)."""
from __future__ import annotations

import logging
from typing import Any, Optional

from config import DATABASE_URL, postgres_ssl_kw
from database.connection import PostgresDbConn

logger = logging.getLogger(__name__)

_pool: Optional[Any] = None

PG_DDL_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS users (
        id BIGSERIAL PRIMARY KEY,
        telegram_id BIGINT UNIQUE NOT NULL,
        language TEXT DEFAULT 'ru',
        timezone TEXT DEFAULT 'Europe/Moscow',
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS events (
        id BIGSERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        title TEXT NOT NULL,
        description TEXT,
        event_datetime TIMESTAMPTZ NOT NULL,
        timezone TEXT NOT NULL,
        recurrence_type TEXT,
        recurrence_value TEXT,
        is_completed INTEGER DEFAULT 0,
        notified_at TIMESTAMPTZ,
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        is_cancelled INTEGER DEFAULT 0,
        cancelled_at TIMESTAMPTZ,
        completed_at TIMESTAMPTZ,
        nudge_count INTEGER DEFAULT 0
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_events_user_datetime ON events(user_id, event_datetime)",
    "CREATE INDEX IF NOT EXISTS idx_events_pending ON events(user_id, is_completed, event_datetime)",
]


async def _get_pool():
    global _pool
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set (PostgreSQL required).")
    if _pool is None:
        import asyncpg

        ssl_kw = postgres_ssl_kw()
        _pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=1,
            max_size=10,
            **ssl_kw,
        )
        logger.info("PostgreSQL connection pool created")
    return _pool


async def get_db():
    """New connection from pool; caller must await close()."""
    pool = await _get_pool()
    raw = await pool.acquire()
    return PostgresDbConn(raw, pool)


async def migrate_events_table_postgres(conn: PostgresDbConn) -> None:
    rows = await conn.fetchall(
        """
        SELECT column_name FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'events'
        """
    )
    if not rows:
        return
    existing = {r[0] for r in rows}
    alters = [
        ("is_cancelled", "INTEGER DEFAULT 0"),
        ("cancelled_at", "TIMESTAMPTZ"),
        ("completed_at", "TIMESTAMPTZ"),
        ("nudge_count", "INTEGER DEFAULT 0"),
    ]
    for col_name, col_def in alters:
        if col_name not in existing:
            await conn.execute(f"ALTER TABLE events ADD COLUMN {col_name} {col_def}")


async def init_schema_postgres() -> None:
    """Create/update PostgreSQL schema."""
    pool = await _get_pool()
    raw = await pool.acquire()
    conn = PostgresDbConn(raw, pool)
    try:
        for stmt in PG_DDL_STATEMENTS:
            await conn.execute(stmt.strip())
        await migrate_events_table_postgres(conn)
    finally:
        await conn.close()


async def init_schema(conn: PostgresDbConn) -> None:
    """Apply schema on an existing wrapped connection (e.g. tests)."""
    for stmt in PG_DDL_STATEMENTS:
        await conn.execute(stmt.strip())
    await migrate_events_table_postgres(conn)


async def init_db() -> None:
    """Startup: create tables if needed."""
    await init_schema_postgres()
    logger.info("PostgreSQL schema ready")


async def close_pool() -> None:
    """Close pool (tests / shutdown)."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


async def close_db(conn: PostgresDbConn) -> None:
    await conn.close()
