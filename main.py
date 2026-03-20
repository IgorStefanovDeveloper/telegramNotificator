"""Telegram Event Reminder Bot - main entry point."""
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

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


async def setup_bot_commands(bot: Bot) -> None:
    """Команды в меню Telegram (/) — видны даже без reply-клавиатуры."""
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Меню и кнопки"),
            BotCommand(command="new", description="Новое событие"),
            BotCommand(command="list", description="Грядущие"),
            BotCommand(command="done", description="Выполненные"),
            BotCommand(command="cancelled", description="Отменённые"),
            BotCommand(command="settings", description="Настройки"),
            BotCommand(command="help", description="Справка"),
        ]
    )


async def main():
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set. Copy .env.example to .env and add your token.")
        sys.exit(1)
    if not DATABASE_URL:
        logger.error("DATABASE_URL is not set. Add PostgreSQL (Railway) or local Postgres URL.")
        sys.exit(1)

    await init_db()
    logger.info("Database: PostgreSQL")

    bot = Bot(
        token=TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    await setup_bot_commands(bot)

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
