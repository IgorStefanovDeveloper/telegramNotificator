"""Configuration loaded from environment variables."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", "./data/events.db"))
DEFAULT_TIMEZONE = "Europe/Moscow"  # MSK
MAX_FUTURE_MONTHS = 24  # Show events for next N months (up to 2 years)
