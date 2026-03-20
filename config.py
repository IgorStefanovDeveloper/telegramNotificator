"""Configuration loaded from environment variables."""
import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
# PostgreSQL only (Railway sets DATABASE_URL).
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
DEFAULT_TIMEZONE = "Europe/Moscow"  # MSK
MAX_FUTURE_MONTHS = 24  # Show events for next N months (up to 2 years)

# IANA id → подписи для кнопок настроек (Вьетнам = единый пояс Asia/Ho_Chi_Minh, Нячанг)
USER_SELECTABLE_TIMEZONES: tuple[tuple[str, str, str], ...] = (
    ("Europe/Moscow", "Москва (UTC+3)", "Moscow (UTC+3)"),
    ("Asia/Ho_Chi_Minh", "Нячанг / Вьетнам (UTC+7)", "Nha Trang, Vietnam (UTC+7)"),
)


def timezone_labels_for_lang(lang: str) -> list[tuple[str, str]]:
    """[(iana_id, кнопка), ...]"""
    return [(row[0], row[1] if lang == "ru" else row[2]) for row in USER_SELECTABLE_TIMEZONES]


def timezone_display(lang: str, iana: str) -> str:
    """Краткое имя пояса для текста."""
    for zid, ru, en in USER_SELECTABLE_TIMEZONES:
        if zid == iana:
            return ru if lang == "ru" else en
    return iana.replace("_", " ").split("/")[-1]


def postgres_ssl_kw() -> dict:
    """asyncpg SSL for managed Postgres (Railway, etc.). Disable for local PG: DATABASE_SSL=0."""
    val = os.getenv("DATABASE_SSL", "1").lower()
    if val in ("0", "false", "no", "off"):
        return {}
    return {"ssl": "require"}
