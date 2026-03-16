"""Scheduler: check events and send notifications every minute."""
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config import DEFAULT_TIMEZONE
from database.db import get_db
from database.events_repo import get_events_to_notify, mark_notified
from i18n import t
from keyboards import notification_actions_kb


def _format_datetime(dt, timezone_str: str = DEFAULT_TIMEZONE) -> str:
    try:
        import pytz
        tz = pytz.timezone(timezone_str)
        if dt.tzinfo is None:
            dt = tz.localize(dt)
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return dt.strftime("%d.%m.%Y %H:%M") if hasattr(dt, 'strftime') else str(dt)


async def _get_user_lang(user_db_id: int) -> str:
    conn = await get_db()
    try:
        cursor = await conn.execute(
            "SELECT language FROM users WHERE id = ?", (user_db_id,)
        )
        row = await cursor.fetchone()
        return row[0] if row else "ru"
    finally:
        await conn.close()


async def send_notifications(bot):
    """Check pending events and send notifications. Called every minute."""
    conn = await get_db()
    try:
        now = datetime.now()
        events_data = await get_events_to_notify(conn, now)
        for telegram_id, user_db_id, event in events_data:
            try:
                lang = await _get_user_lang(user_db_id)
                dt_str = _format_datetime(event.event_datetime, event.timezone)
                text = t(lang, "notification", title=event.title, datetime=dt_str)
                kb = notification_actions_kb(event.id, lang)
                await bot.send_message(
                    telegram_id,
                    text,
                    parse_mode="HTML",
                    reply_markup=kb,
                )
                await mark_notified(conn, event.id, now)
            except Exception as e:
                print(f"Failed to notify {telegram_id} for event {event.id}: {e}")
    finally:
        await conn.close()


def start_scheduler(bot):
    """Start APScheduler to run send_notifications every minute."""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        send_notifications,
        IntervalTrigger(minutes=1),
        args=[bot],
        id="notify_events",
    )
    scheduler.start()
    return scheduler
