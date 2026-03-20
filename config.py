"""Configuration loaded from environment variables."""
import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
# PostgreSQL only (Railway sets DATABASE_URL).
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
DEFAULT_TIMEZONE = "Europe/Moscow"  # MSK
MAX_FUTURE_MONTHS = 24  # Show events for next N months (up to 2 years)


def postgres_ssl_kw() -> dict:
    """asyncpg SSL for managed Postgres (Railway, etc.). Disable for local PG: DATABASE_SSL=0."""
    val = os.getenv("DATABASE_SSL", "1").lower()
    if val in ("0", "false", "no", "off"):
        return {}
    return {"ssl": "require"}
