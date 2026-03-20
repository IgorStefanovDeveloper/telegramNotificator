"""Telegram Event Reminder Bot - main entry point."""
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import DATABASE_URL, TELEGRAM_BOT_TOKEN
from database.db import init_db
from handlers import router
from scheduler import start_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


async def main():
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set. Copy .env.example to .env and add your token.")
        sys.exit(1)

    await init_db()
    if DATABASE_URL:
        logger.info("Database: PostgreSQL (DATABASE_URL)")
    else:
        logger.info("Database: SQLite file")

    bot = Bot(
        token=TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(router)

    scheduler = start_scheduler(bot)
    logger.info("Scheduler started. Bot is running...")

    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
