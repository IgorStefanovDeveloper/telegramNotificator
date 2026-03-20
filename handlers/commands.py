"""Command handlers: /start, /help, /list, /done, /cancelled, /settings."""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import DEFAULT_TIMEZONE
from database.db import get_db
from database.events_repo import (
    get_or_create_user,
    get_user_settings,
    get_user_events_upcoming,
    get_user_events_completed,
    get_user_events_cancelled,
)
from database.models import RECURRENCE_NONE, RECURRENCE_MONTHLY, RECURRENCE_WEEKLY
from i18n import t
from keyboards import main_menu, settings_kb, list_events_kb

router = Router()


def _recurrence_text(lang: str, rec_type: str, rec_value: str) -> str:
    if rec_type == RECURRENCE_NONE:
        return t(lang, "recurrence_once")
    if rec_type == RECURRENCE_WEEKLY and rec_value:
        days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        try:
            idx = int(rec_value)
            day = t(lang, days[idx])
            return t(lang, "recurrence_weekly", day=day)
        except (ValueError, IndexError):
            pass
    if rec_type == RECURRENCE_MONTHLY and rec_value:
        return t(lang, "recurrence_monthly", day=rec_value)
    return t(lang, "recurrence_once")


def _format_datetime(dt_utc, timezone_str: str = DEFAULT_TIMEZONE) -> str:
    """Format UTC-stored datetime for display in user TZ."""
    from utils_timezone import format_utc_for_display
    return format_utc_for_display(dt_utc, timezone_str)


@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    conn = await get_db()
    try:
        await get_or_create_user(conn, user_id)
        lang, _ = await get_user_settings(conn, user_id) or (None, None)
        lang = lang or "ru"
        await message.answer(
            t(lang, "welcome"),
            reply_markup=main_menu(lang),
            parse_mode="HTML",
        )
    finally:
        await conn.close()


@router.message(Command("help"))
async def cmd_help(message: Message):
    conn = await get_db()
    try:
        lang, _ = await get_user_settings(conn, message.from_user.id) or ("ru", None)
        await message.answer(t(lang, "help"), parse_mode="HTML")
    finally:
        await conn.close()


@router.message(Command("settings"), F.text)
@router.message(F.text.in_({"⚙️ Настройки", "⚙️ Settings"}))
async def cmd_settings(message: Message, state: FSMContext):
    await state.clear()
    conn = await get_db()
    try:
        await get_or_create_user(conn, message.from_user.id)
        lang, tz = await get_user_settings(conn, message.from_user.id) or ("ru", DEFAULT_TIMEZONE)
        lang_display = "Русский" if lang == "ru" else "English"
        tz_short = tz.split("/")[-1].replace("_", " ")
        await message.answer(
            t(lang, "settings", language=lang_display, timezone=tz_short),
            reply_markup=settings_kb(lang),
            parse_mode="HTML",
        )
    finally:
        await conn.close()


@router.message(Command("list"), F.text)
@router.message(F.text.in_({"📅 Список событий", "📅 List events"}))
async def cmd_list(message: Message, state: FSMContext):
    from datetime import datetime, timedelta
    from config import MAX_FUTURE_MONTHS

    await state.clear()
    conn = await get_db()
    try:
        user_db_id = await get_or_create_user(conn, message.from_user.id)
        lang, tz = await get_user_settings(conn, message.from_user.id) or ("ru", DEFAULT_TIMEZONE)
        from utils_timezone import utc_now
        now = utc_now()
        to_dt = now + timedelta(days=30 * MAX_FUTURE_MONTHS)
        events = await get_user_events_upcoming(conn, user_db_id, now, to_dt)
        if not events:
            await message.answer(t(lang, "list_empty"), parse_mode="HTML")
            return
        lines = []
        for ev in events:
            dt_str = _format_datetime(ev.event_datetime, ev.timezone)
            if ev.recurrence_type == RECURRENCE_WEEKLY and ev.recurrence_value:
                days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
                try:
                    day = t(lang, days[int(ev.recurrence_value)])
                    lines.append(t(lang, "event_item_recurring_weekly", day=day, title=ev.title, datetime=dt_str))
                except (ValueError, IndexError):
                    lines.append(t(lang, "event_item", title=ev.title, datetime=dt_str, recurrence_line=_recurrence_text(lang, ev.recurrence_type, ev.recurrence_value or "")))
            elif ev.recurrence_type == RECURRENCE_MONTHLY and ev.recurrence_value:
                lines.append(t(lang, "event_item_recurring_monthly", day=ev.recurrence_value, title=ev.title, datetime=dt_str))
            else:
                rec_line = _recurrence_text(lang, ev.recurrence_type, ev.recurrence_value or "")
                lines.append(t(lang, "event_item", title=ev.title, datetime=dt_str, recurrence_line=rec_line))
        text = t(lang, "list_upcoming", events="\n".join(lines))
        await message.answer(
            text,
            parse_mode="HTML",
            reply_markup=list_events_kb(events, lang),
        )
    finally:
        await conn.close()


@router.message(Command("done"))
async def cmd_done(message: Message, state: FSMContext):
    await state.clear()
    conn = await get_db()
    try:
        user_db_id = await get_or_create_user(conn, message.from_user.id)
        lang, _ = await get_user_settings(conn, message.from_user.id) or ("ru", DEFAULT_TIMEZONE)
        events = await get_user_events_completed(conn, user_db_id, limit=30)
        if not events:
            await message.answer(t(lang, "list_history_empty"), parse_mode="HTML")
            return
        lines = []
        for ev in events:
            dt_str = _format_datetime(ev.event_datetime, ev.timezone)
            lines.append(
                t(
                    lang,
                    "event_item",
                    title=ev.title,
                    datetime=dt_str,
                    recurrence_line=_recurrence_text(lang, ev.recurrence_type, ev.recurrence_value or ""),
                )
            )
        await message.answer(t(lang, "list_completed", events="\n".join(lines)), parse_mode="HTML")
    finally:
        await conn.close()


@router.message(Command("cancelled"))
async def cmd_cancelled(message: Message, state: FSMContext):
    await state.clear()
    conn = await get_db()
    try:
        user_db_id = await get_or_create_user(conn, message.from_user.id)
        lang, _ = await get_user_settings(conn, message.from_user.id) or ("ru", DEFAULT_TIMEZONE)
        events = await get_user_events_cancelled(conn, user_db_id, limit=30)
        if not events:
            await message.answer(t(lang, "list_history_empty"), parse_mode="HTML")
            return
        lines = []
        for ev in events:
            dt_str = _format_datetime(ev.event_datetime, ev.timezone)
            lines.append(
                t(
                    lang,
                    "event_item",
                    title=ev.title,
                    datetime=dt_str,
                    recurrence_line=_recurrence_text(lang, ev.recurrence_type, ev.recurrence_value or ""),
                )
            )
        await message.answer(t(lang, "list_cancelled", events="\n".join(lines)), parse_mode="HTML")
    finally:
        await conn.close()
