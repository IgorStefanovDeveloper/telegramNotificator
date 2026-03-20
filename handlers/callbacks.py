"""Callback handlers: event actions (done, postpone, delete), settings."""
from aiogram import Router, F
from aiogram.types import CallbackQuery

from config import DEFAULT_TIMEZONE, USER_SELECTABLE_TIMEZONES, timezone_display
from database.db import get_db
from database.events_repo import (
    get_event_by_id,
    mark_completed,
    postpone_event,
    mark_cancelled,
    delete_event,
    get_or_create_user,
    get_user_settings,
    update_user_language,
    update_user_timezone,
)
from database.models import RECURRENCE_NONE
from i18n import t
from keyboards import main_menu, settings_kb

router = Router()


@router.callback_query(F.data.startswith("ev:done:"))
async def cb_event_done(cb: CallbackQuery):
    await cb.answer()
    event_id = int(cb.data.split(":")[2])
    conn = await get_db()
    try:
        event = await get_event_by_id(conn, event_id)
        if not event:
            await cb.answer("Событие не найдено." if cb.message else "Event not found.", show_alert=True)
            return
        user_db_id = await get_or_create_user(conn, cb.from_user.id)
        if event.user_id != user_db_id:
            await cb.answer("Нет доступа." if cb.message else "No access.", show_alert=True)
            return
        lang, _ = await get_user_settings(conn, cb.from_user.id) or ("ru", DEFAULT_TIMEZONE)
        if event.recurrence_type != RECURRENCE_NONE:
            # Следующее вхождение уже сдвинуто при отправке уведомления (scheduler)
            text = t(lang, "event_done")
        else:
            await mark_completed(conn, event_id)
            text = t(lang, "event_done")
        try:
            await cb.message.edit_text(cb.message.text + "\n\n✅ " + text)
        except Exception:
            await cb.message.answer(text)
    finally:
        await conn.close()


@router.callback_query(F.data.startswith("ev:postpone:"))
async def cb_event_postpone(cb: CallbackQuery):
    await cb.answer()
    event_id = int(cb.data.split(":")[2])
    conn = await get_db()
    try:
        event = await get_event_by_id(conn, event_id)
        if not event:
            await cb.answer("Событие не найдено.", show_alert=True)
            return
        user_db_id = await get_or_create_user(conn, cb.from_user.id)
        if event.user_id != user_db_id:
            await cb.answer("Нет доступа.", show_alert=True)
            return
        await postpone_event(conn, event_id, hours=1)
        lang, _ = await get_user_settings(conn, cb.from_user.id) or ("ru", DEFAULT_TIMEZONE)
        try:
            await cb.message.edit_text(cb.message.text + "\n\n⏰ " + t(lang, "event_postponed"))
        except Exception:
            await cb.message.answer(t(lang, "event_postponed"))
    finally:
        await conn.close()


@router.callback_query(F.data.startswith("ev:cancel:"))
async def cb_event_cancel(cb: CallbackQuery):
    """Soft cancel from notification (keeps history)."""
    event_id = int(cb.data.split(":")[2])
    conn = await get_db()
    try:
        event = await get_event_by_id(conn, event_id)
        if not event:
            await cb.answer("Событие не найдено.", show_alert=True)
            return
        user_db_id = await get_or_create_user(conn, cb.from_user.id)
        if event.user_id != user_db_id:
            await cb.answer("Нет доступа.", show_alert=True)
            return
        await mark_cancelled(conn, event_id)
        lang, _ = await get_user_settings(conn, cb.from_user.id) or ("ru", DEFAULT_TIMEZONE)
        await cb.answer()
        try:
            await cb.message.edit_text(cb.message.text + "\n\n🚫 " + t(lang, "event_cancelled"))
        except Exception:
            await cb.message.answer(t(lang, "event_cancelled"))
    finally:
        await conn.close()


@router.callback_query(F.data.startswith("ev:del:"))
async def cb_event_delete(cb: CallbackQuery):
    await cb.answer()
    event_id = int(cb.data.split(":")[2])
    conn = await get_db()
    try:
        event = await get_event_by_id(conn, event_id)
        if not event:
            await cb.answer("Событие не найдено.", show_alert=True)
            return
        user_db_id = await get_or_create_user(conn, cb.from_user.id)
        if event.user_id != user_db_id:
            await cb.answer("Нет доступа.", show_alert=True)
            return
        await delete_event(conn, event_id)
        lang, _ = await get_user_settings(conn, cb.from_user.id) or ("ru", DEFAULT_TIMEZONE)
        try:
            await cb.message.edit_text(cb.message.text + "\n\n🗑 " + t(lang, "event_deleted"))
        except Exception:
            await cb.message.answer(t(lang, "event_deleted"))
    finally:
        await conn.close()


@router.callback_query(F.data.startswith("set:lang:"))
async def cb_set_lang(cb: CallbackQuery):
    await cb.answer()
    lang = cb.data.split(":")[2]
    conn = await get_db()
    try:
        await get_or_create_user(conn, cb.from_user.id)
        await update_user_language(conn, cb.from_user.id, lang)
        _, tz = await get_user_settings(conn, cb.from_user.id) or ("ru", DEFAULT_TIMEZONE)
        tz_short = timezone_display(lang, tz)
        lang_display = "Русский" if lang == "ru" else "English"
        await cb.message.edit_text(
            t(lang, "settings", language=lang_display, timezone=tz_short),
            reply_markup=settings_kb(lang),
            parse_mode="HTML",
        )
        # Reply-клавиатуру нельзя «отредактировать» — присылаем новую с текстом кнопок на выбранном языке
        await cb.message.answer(t(lang, "lang_changed"), reply_markup=main_menu(lang))
    finally:
        await conn.close()


@router.callback_query(F.data.startswith("set:tz:"))
async def cb_set_timezone(cb: CallbackQuery):
    await cb.answer()
    try:
        idx = int(cb.data.split(":")[2])
    except (IndexError, ValueError):
        return
    if idx < 0 or idx >= len(USER_SELECTABLE_TIMEZONES):
        return
    tz_iana = USER_SELECTABLE_TIMEZONES[idx][0]
    conn = await get_db()
    try:
        await get_or_create_user(conn, cb.from_user.id)
        await update_user_timezone(conn, cb.from_user.id, tz_iana)
        lang, tz = await get_user_settings(conn, cb.from_user.id) or ("ru", DEFAULT_TIMEZONE)
        tz_short = timezone_display(lang, tz)
        lang_display = "Русский" if lang == "ru" else "English"
        await cb.message.edit_text(
            t(lang, "settings", language=lang_display, timezone=tz_short),
            reply_markup=settings_kb(lang),
            parse_mode="HTML",
        )
        await cb.message.answer(
            t(lang, "timezone_changed"),
            reply_markup=main_menu(lang),
        )
    finally:
        await conn.close()
