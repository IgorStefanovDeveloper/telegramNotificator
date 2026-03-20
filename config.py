"""Configuration loaded from environment variables."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
# PostgreSQL (Railway sets DATABASE_URL). If set, SQLite file is ignored.
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", "./data/events.db"))
DEFAULT_TIMEZONE = "Europe/Moscow"  # MSK
MAX_FUTURE_MONTHS = 24  # Show events for next N months (up to 2 years)


def postgres_ssl_kw() -> dict:
    """asyncpg SSL for managed Postgres (Railway, etc.). Disable for local PG: DATABASE_SSL=0."""
    val = os.getenv("DATABASE_SSL", "1").lower()
    if val in ("0", "false", "no", "off"):
        return {}
    return {"ssl": "require"}
