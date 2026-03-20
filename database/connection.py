"""Unified async DB API: SQLite (aiosqlite) or PostgreSQL (asyncpg)."""
from __future__ import annotations

import re
from typing import Any, Optional, Protocol, Tuple, runtime_checkable

import aiosqlite


def sql_qmarks_to_dollar(sql: str) -> str:
    """Convert ? placeholders to $1, $2, ... for PostgreSQL."""
    n = 0

    def repl(_m: re.Match) -> str:
        nonlocal n
        n += 1
        return f"${n}"

    return re.sub(r"\?", repl, sql)


def _parse_asyncpg_rowcount(status: str) -> int:
    """Parse 'UPDATE 1', 'DELETE 3', etc."""
    if not status:
        return 0
    parts = status.split()
    try:
        return int(parts[-1])
    except (ValueError, IndexError):
        return 0


@runtime_checkable
class DbConn(Protocol):
    """Connection used by events_repo and handlers."""

    async def fetchone(self, sql: str, args: Tuple[Any, ...] = ()) -> Optional[tuple]: ...

    async def fetchall(self, sql: str, args: Tuple[Any, ...] = ()) -> list[tuple]: ...

    async def execute(self, sql: str, args: Tuple[Any, ...] = ()) -> None: ...

    async def execute_rowcount(self, sql: str, args: Tuple[Any, ...] = ()) -> int: ...

    async def execute_insert_returning_id(self, sql: str, args: Tuple[Any, ...] = ()) -> int: ...

    async def close(self) -> None: ...


class SqliteDbConn:
    """aiosqlite with shared API."""

    def __init__(self, conn: aiosqlite.Connection):
        self._conn = conn

    async def fetchone(self, sql: str, args: Tuple[Any, ...] = ()) -> Optional[tuple]:
        cursor = await self._conn.execute(sql, args)
        row = await cursor.fetchone()
        return tuple(row) if row is not None else None

    async def fetchall(self, sql: str, args: Tuple[Any, ...] = ()) -> list[tuple]:
        cursor = await self._conn.execute(sql, args)
        rows = await cursor.fetchall()
        return [tuple(r) for r in rows]

    async def execute(self, sql: str, args: Tuple[Any, ...] = ()) -> None:
        await self._conn.execute(sql, args)
        await self._conn.commit()

    async def execute_rowcount(self, sql: str, args: Tuple[Any, ...] = ()) -> int:
        cursor = await self._conn.execute(sql, args)
        await self._conn.commit()
        return cursor.rowcount or 0

    async def execute_insert_returning_id(self, sql: str, args: Tuple[Any, ...] = ()) -> int:
        cursor = await self._conn.execute(sql, args)
        row = await cursor.fetchone()
        await self._conn.commit()
        if not row:
            raise RuntimeError("INSERT RETURNING id returned no row")
        return int(row[0])

    async def close(self) -> None:
        await self._conn.close()


class PostgresDbConn:
    """Single asyncpg connection from pool (release on close)."""

    def __init__(self, raw_conn: Any, pool: Any):
        self._conn = raw_conn
        self._pool = pool

    async def fetchone(self, sql: str, args: Tuple[Any, ...] = ()) -> Optional[tuple]:
        q = sql_qmarks_to_dollar(sql)
        row = await self._conn.fetchrow(q, *args)
        return tuple(row) if row is not None else None

    async def fetchall(self, sql: str, args: Tuple[Any, ...] = ()) -> list[tuple]:
        q = sql_qmarks_to_dollar(sql)
        rows = await self._conn.fetch(q, *args)
        return [tuple(r) for r in rows]

    async def execute(self, sql: str, args: Tuple[Any, ...] = ()) -> None:
        q = sql_qmarks_to_dollar(sql)
        await self._conn.execute(q, *args)

    async def execute_rowcount(self, sql: str, args: Tuple[Any, ...] = ()) -> int:
        q = sql_qmarks_to_dollar(sql)
        status = await self._conn.execute(q, *args)
        return _parse_asyncpg_rowcount(status)

    async def execute_insert_returning_id(self, sql: str, args: Tuple[Any, ...] = ()) -> int:
        q = sql_qmarks_to_dollar(sql)
        row = await self._conn.fetchrow(q, *args)
        if not row:
            raise RuntimeError("INSERT RETURNING id returned no row")
        return int(row[0])

    async def close(self) -> None:
        await self._pool.release(self._conn)
