"""Scheduler: check events and send notifications every minute."""
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config import DEFAULT_TIMEZONE, timezone_display
from database.db import get_db
from database.events_repo import (
    get_events_to_notify,
    get_events_to_nudge,
    mark_notified,
    record_nudge_sent,
    advance_recurring_event,
)
from database.models import RECURRENCE_NONE
from i18n import t
from keyboards import notification_actions_kb


def _format_datetime(dt_utc, timezone_str: str = DEFAULT_TIMEZONE) -> str:
    from utils_timezone import format_utc_for_display
    return format_utc_for_display(dt_utc, timezone_str)


async def _get_user_lang(user_db_id: int) -> str:
    conn = await get_db()
    try:
        row = await conn.fetchone("SELECT language FROM users WHERE id = ?", (user_db_id,))
        return row[0] if row else "ru"
    finally:
        await conn.close()


async def _send_one_notification(bot, telegram_id: int, user_db_id: int, event, now: datetime) -> None:
    lang = await _get_user_lang(user_db_id)
    dt_str = _format_datetime(event.event_datetime, event.timezone)
    zone_hint = t(lang, "notification_zone_hint", zone=timezone_display(lang, event.timezone))
    text = t(lang, "notification", title=event.title, datetime=dt_str, zone_hint=zone_hint)
    kb = notification_actions_kb(event.id, lang)
    await bot.send_message(
        telegram_id,
        text,
        parse_mode="HTML",
        reply_markup=kb,
    )
    if event.recurrence_type != RECURRENCE_NONE:
        conn = await get_db()
        try:
            await advance_recurring_event(conn, event)
        finally:
            await conn.close()
    else:
        conn = await get_db()
        try:
            await mark_notified(conn, event.id, now)
        finally:
            await conn.close()


async def _send_nudge(bot, telegram_id: int, user_db_id: int, event, now: datetime) -> None:
    lang = await _get_user_lang(user_db_id)
    dt_str = _format_datetime(event.event_datetime, event.timezone)
    zone_hint = t(lang, "notification_zone_hint", zone=timezone_display(lang, event.timezone))
    text = t(lang, "notification_nudge", title=event.title, datetime=dt_str, zone_hint=zone_hint)
    kb = notification_actions_kb(event.id, lang)
    await bot.send_message(
        telegram_id,
        text,
        parse_mode="HTML",
        reply_markup=kb,
    )
    conn = await get_db()
    try:
        await record_nudge_sent(conn, event.id, now)
    finally:
        await conn.close()


async def send_notifications(bot):
    """First notifications + follow-up nudges (up to 3 total). Uses UTC."""
    from utils_timezone import utc_now

    conn = await get_db()
    try:
        now = utc_now()
        events_data = await get_events_to_notify(conn, now)
        for telegram_id, user_db_id, event in events_data:
            try:
                await _send_one_notification(bot, telegram_id, user_db_id, event, now)
            except Exception as e:
                print(f"Failed to notify {telegram_id} for event {event.id}: {e}")

        nudge_data = await get_events_to_nudge(conn, now)
        for telegram_id, user_db_id, event in nudge_data:
            try:
                await _send_nudge(bot, telegram_id, user_db_id, event, now)
            except Exception as e:
                print(f"Failed nudge {telegram_id} for event {event.id}: {e}")
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
