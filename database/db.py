"""Database connection and initialization."""
import aiosqlite
from pathlib import Path

from config import DATABASE_PATH


async def get_db():
    """Get database connection."""
    path = DATABASE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    return await aiosqlite.connect(path)


SCHEMA_SQL = """
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


async def init_schema(conn) -> None:
    """Run schema on given connection. Used by init_db and tests."""
    await conn.executescript(SCHEMA_SQL)
    await conn.commit()
    await migrate_events_table(conn)


async def migrate_events_table(conn) -> None:
    """Additive migrations only — never DROP data. Safe for existing DBs."""
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


async def init_db():
    """Create tables if they don't exist."""
    conn = await get_db()
    try:
        await init_schema(conn)
    finally:
        await conn.close()


async def close_db(conn):
    """Close database connection."""
    await conn.close()
