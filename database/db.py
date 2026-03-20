"""Database connection, pool, and schema init (SQLite or PostgreSQL)."""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Optional

import aiosqlite

from config import DATABASE_PATH, DATABASE_URL, postgres_ssl_kw
from database.connection import PostgresDbConn, SqliteDbConn

logger = logging.getLogger(__name__)

_pool: Optional[Any] = None

SCHEMA_SQLITE = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        telegram_id INTEGER UNIQUE NOT NULL,
        language TEXT DEFAULT 'ru',
        timezone TEXT DEFAULT 'Europe/Moscow',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        event_datetime TIMESTAMP NOT NULL,
        timezone TEXT NOT NULL,
        recurrence_type TEXT,
        recurrence_value TEXT,
        is_completed INTEGER DEFAULT 0,
        notified_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_cancelled INTEGER DEFAULT 0,
        cancelled_at TEXT,
        completed_at TEXT,
        nudge_count INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );

    CREATE INDEX IF NOT EXISTS idx_events_user_datetime ON events(user_id, event_datetime);
    CREATE INDEX IF NOT EXISTS idx_events_pending ON events(user_id, is_completed, event_datetime);
"""

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


def _use_postgres() -> bool:
    return bool(DATABASE_URL and DATABASE_URL.strip())


async def _get_pool():
    global _pool
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
    """New connection per call; caller must await close()."""
    if _use_postgres():
        pool = await _get_pool()
        raw = await pool.acquire()
        return PostgresDbConn(raw, pool)
    path = DATABASE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = await aiosqlite.connect(path)
    return SqliteDbConn(raw)


async def init_sqlite_schema_raw(conn: aiosqlite.Connection) -> None:
    """Initialize SQLite schema on a raw connection (tests / file init)."""
    await conn.executescript(SCHEMA_SQLITE)
    await conn.commit()
    await migrate_events_table_sqlite(conn)


async def migrate_events_table_sqlite(conn: aiosqlite.Connection) -> None:
    cursor = await conn.execute("PRAGMA table_info(events)")
    rows = await cursor.fetchall()
    if not rows:
        return
    existing = {r[1] for r in rows}
    alters = [
        ("is_cancelled", "INTEGER DEFAULT 0"),
        ("cancelled_at", "TEXT"),
        ("completed_at", "TEXT"),
        ("nudge_count", "INTEGER DEFAULT 0"),
    ]
    for col_name, col_def in alters:
        if col_name not in existing:
            await conn.execute(f"ALTER TABLE events ADD COLUMN {col_name} {col_def}")
    await conn.commit()


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


async def init_schema_sqlite_file() -> None:
    """Create/update SQLite file at DATABASE_PATH."""
    path = DATABASE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = await aiosqlite.connect(path)
    try:
        await init_sqlite_schema_raw(conn)
    finally:
        await conn.close()


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


async def init_schema(conn: SqliteDbConn | PostgresDbConn) -> None:
    """Run schema on a wrapped connection (e.g. in-memory tests)."""
    if isinstance(conn, SqliteDbConn):
        await init_sqlite_schema_raw(conn._conn)
        return
    for stmt in PG_DDL_STATEMENTS:
        await conn.execute(stmt.strip())
    await migrate_events_table_postgres(conn)


async def init_db() -> None:
    """Startup: create tables if needed."""
    if _use_postgres():
        await init_schema_postgres()
        logger.info("PostgreSQL schema ready")
    else:
        await init_schema_sqlite_file()
        logger.info("SQLite schema ready at %s", DATABASE_PATH.resolve())


async def close_db(conn: SqliteDbConn | PostgresDbConn) -> None:
    await conn.close()
