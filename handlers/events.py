"""Event creation FSM and handlers."""
import logging
from datetime import datetime
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from aiogram_calendar.schemas import SimpleCalAct

logger = logging.getLogger(__name__)

from config import DEFAULT_TIMEZONE
from database.db import get_db
from utils_timezone import format_utc_for_display, local_to_utc, utc_now
from database.events_repo import (
    get_or_create_user,
    create_event,
    get_user_settings,
    get_event_by_id,
    update_event,
)
from database.models import RECURRENCE_NONE, RECURRENCE_MONTHLY, RECURRENCE_WEEKLY
from i18n import t
from keyboards import (
    recurrence_kb,
    weekly_days_kb,
    cancel_kb,
    datetime_calendar_kb,
    edit_field_kb,
    edit_recurrence_kb,
    edit_weekly_days_kb,
)

router = Router()


class AddEventStates(StatesGroup):
    title = State()
    datetime = State()
    datetime_time = State()  # After calendar date selected, waiting for HH:MM
    recurrence = State()
    weekly_day = State()
    monthly_day = State()


class EditEventStates(StatesGroup):
    choose_field = State()
    edit_title = State()
    edit_datetime = State()
    edit_datetime_time = State()  # After calendar date selected
    edit_recurrence = State()
    edit_weekly_day = State()
    edit_monthly_day = State()


def _parse_time(text: str) -> tuple[int, int] | None:
    """Parse HH:MM or H:MM. Returns (hour, minute) or None."""
    try:
        text = (text or "").strip()
        if ":" not in text:
            return None
        parts = text.split(":")
        if len(parts) != 2:
            return None
        h, m = int(parts[0]), int(parts[1])
        if 0 <= h <= 23 and 0 <= m <= 59:
            return (h, m)
        return None
    except (ValueError, IndexError):
        return None


def _parse_datetime(text: str) -> datetime | None:
    """Parse DD.MM.YYYY HH:MM"""
    try:
        parts = text.strip().split()
        if len(parts) != 2:
            return None
        d, t_part = parts[0], parts[1]
        day, month, year = map(int, d.split("."))
        hour, minute = map(int, t_part.split(":"))
        return datetime(year, month, day, hour, minute)
    except (ValueError, IndexError):
        return None


@router.message(Command("new"))
@router.message(F.text.in_({"➕ Новое событие", "➕ New event"}))
async def cmd_new_event(message: Message, state: FSMContext):
    conn = await get_db()
    try:
        await get_or_create_user(conn, message.from_user.id)
        lang, tz = await get_user_settings(conn, message.from_user.id) or ("ru", DEFAULT_TIMEZONE)
        await state.clear()
        await state.set_state(AddEventStates.title)
        await state.update_data(timezone=tz, lang=lang)
        await message.answer(
            t(lang, "ask_event_title"),
            reply_markup=cancel_kb(lang),
        )
    finally:
        await conn.close()


@router.message(AddEventStates.title, F.text)
async def process_title(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    if not message.text or len(message.text.strip()) < 2:
        await message.answer("Введи название (минимум 2 символа)." if lang == "ru" else "Enter title (min 2 chars).")
        return
    await state.update_data(title=message.text.strip())
    await state.set_state(AddEventStates.datetime)
    await message.answer(
        t(lang, "ask_event_datetime"),
        reply_markup=datetime_calendar_kb(lang),
    )


@router.message(AddEventStates.datetime, F.text)
async def process_datetime(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    dt = _parse_datetime(message.text or "")
    if not dt:
        await message.answer(t(lang, "invalid_datetime"))
        return
    timezone = data.get("timezone", DEFAULT_TIMEZONE)
    from utils_timezone import local_to_utc, utc_now
    dt_utc = local_to_utc(dt, timezone)
    if dt_utc < utc_now():
        await message.answer(t(lang, "datetime_past"))
        return
    await state.update_data(event_datetime=dt)
    await state.set_state(AddEventStates.recurrence)
    await message.answer(
        t(lang, "ask_recurrence"),
        reply_markup=recurrence_kb(lang),
    )


async def _open_calendar(cb: CallbackQuery, lang: str) -> None:
    """Show calendar inline."""
    cal = _make_calendar(lang)
    await cb.message.edit_reply_markup(reply_markup=await cal.start_calendar())


@router.callback_query(F.data == "cal:open")
async def cb_open_calendar(cb: CallbackQuery, state: FSMContext):
    """Show calendar when user clicks the calendar button."""
    current = await state.get_state()
    allowed = ("AddEventStates:datetime", "EditEventStates:edit_datetime")
    if current not in allowed:
        lang = "ru" if (cb.from_user.language_code or "").startswith("ru") else "en"
        await cb.answer(t(lang, "cancelled"), show_alert=True)
        return
    await cb.answer()
    data = await state.get_data()
    lang = data.get("lang", "ru")
    try:
        await _open_calendar(cb, lang)
    except Exception as e:
        logger.exception("Calendar open failed: %s", e)
        await cb.answer("Ошибка календаря. Введите дату вручную." if lang == "ru" else "Calendar error. Enter date manually.", show_alert=True)


def _make_calendar(lang: str):
    """Create SimpleCalendar with locale fallback."""
    cancel_btn = t(lang, "cancel")
    today_btn = "Сегодня" if lang == "ru" else "Today"
    locale_str = "ru_RU" if lang == "ru" else "en_US"
    try:
        return SimpleCalendar(locale=locale_str, cancel_btn=cancel_btn, today_btn=today_btn)
    except Exception as e:
        logger.warning("Calendar locale %s failed: %s", locale_str, e)
        return SimpleCalendar(locale=None, cancel_btn=cancel_btn, today_btn=today_btn)


@router.callback_query(AddEventStates.datetime, SimpleCalendarCallback.filter())
async def cb_calendar_select_add(cb: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    """Process calendar date selection when adding event."""
    data = await state.get_data()
    lang = data.get("lang", "ru")
    cal = _make_calendar(lang)
    selected, date = await cal.process_selection(cb, callback_data)
    if selected and date:
        await state.update_data(calendar_date=date)
        await state.set_state(AddEventStates.datetime_time)
        await cb.message.edit_text(
            t(lang, "ask_event_time"),
            reply_markup=cancel_kb(lang),
        )
    elif callback_data.act == SimpleCalAct.cancel:
        await cb.message.edit_reply_markup(reply_markup=datetime_calendar_kb(lang))


@router.callback_query(EditEventStates.edit_datetime, SimpleCalendarCallback.filter())
async def cb_calendar_select_edit(cb: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    """Process calendar date selection when editing event."""
    data = await state.get_data()
    lang = data.get("lang", "ru")
    cal = _make_calendar(lang)
    selected, date = await cal.process_selection(cb, callback_data)
    if selected and date:
        await state.update_data(calendar_date=date)
        await state.set_state(EditEventStates.edit_datetime_time)
        await cb.message.edit_text(
            t(lang, "ask_event_time"),
            reply_markup=cancel_kb(lang),
        )
    elif callback_data.act == SimpleCalAct.cancel:
        await cb.message.edit_reply_markup(reply_markup=datetime_calendar_kb(lang))


@router.message(AddEventStates.datetime_time, F.text)
async def process_datetime_time(message: Message, state: FSMContext):
    """Parse time (HH:MM) and combine with calendar date."""
    data = await state.get_data()
    lang = data.get("lang", "ru")
    calendar_date = data.get("calendar_date")
    if not calendar_date:
        await state.clear()
        await message.answer(t(lang, "cancelled"))
        return
    parsed = _parse_time(message.text or "")
    if not parsed:
        await message.answer("Введи время в формате ЧЧ:ММ (например 14:30)" if lang == "ru" else "Enter time as HH:MM (e.g. 14:30)")
        return
    hour, minute = parsed
    dt = datetime(calendar_date.year, calendar_date.month, calendar_date.day, hour, minute)
    timezone = data.get("timezone", DEFAULT_TIMEZONE)
    dt_utc = local_to_utc(dt, timezone)
    if dt_utc < utc_now():
        await message.answer(t(lang, "datetime_past"))
        return
    await state.update_data(event_datetime=dt)
    await state.set_state(AddEventStates.recurrence)
    await message.answer(
        t(lang, "ask_recurrence"),
        reply_markup=recurrence_kb(lang),
    )


@router.callback_query(AddEventStates.recurrence, F.data.startswith("rec:"))
async def process_recurrence(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    rec_type = cb.data.split(":")[1]
    data = await state.get_data()
    lang = data.get("lang", "ru")

    if rec_type == "once":
        await _save_event(cb.message, state, RECURRENCE_NONE, None, telegram_id=cb.from_user.id)
        return
    if rec_type == "weekly":
        await state.set_state(AddEventStates.weekly_day)
        await cb.message.edit_text(t(lang, "ask_weekly_day"), reply_markup=weekly_days_kb(lang))
        return
    if rec_type == "monthly":
        await state.set_state(AddEventStates.monthly_day)
        await cb.message.edit_text(t(lang, "ask_monthly_day"), reply_markup=cancel_kb(lang))
        return


@router.callback_query(AddEventStates.weekly_day, F.data.startswith("day:"))
async def process_weekly_day(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    day = cb.data.split(":")[1]
    await _save_event(cb.message, state, RECURRENCE_WEEKLY, day, telegram_id=cb.from_user.id)


@router.message(AddEventStates.monthly_day, F.text)
async def process_monthly_day(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    try:
        day = int(message.text.strip())
        if 1 <= day <= 31:
            await _save_event(message, state, RECURRENCE_MONTHLY, str(day), telegram_id=message.from_user.id)
        else:
            await message.answer(t(lang, "invalid_day"))
    except ValueError:
        await message.answer(t(lang, "invalid_day"))


async def _save_event(message, state: FSMContext, rec_type: str, rec_value: str | None, *, telegram_id: int = None):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    title = data["title"]
    event_datetime = data["event_datetime"]
    timezone = data.get("timezone", DEFAULT_TIMEZONE)

    # CallbackQuery.message has from_user=bot; pass telegram_id explicitly from cb.from_user.id
    user_telegram_id = telegram_id if telegram_id is not None else message.from_user.id

    conn = await get_db()
    try:
        user_db_id = await get_or_create_user(conn, user_telegram_id)
        event_id = await create_event(
            conn,
            user_id=user_db_id,
            title=title,
            event_datetime=event_datetime,
            timezone=timezone,
            recurrence_type=rec_type,
            recurrence_value=rec_value,
        )
        rec_text = _recurrence_text(lang, rec_type, rec_value or "")
        dt_str = event_datetime.strftime("%d.%m.%Y %H:%M")
        summary = t(lang, "event_summary", title=title, datetime=dt_str, recurrence=rec_text)
        text = t(lang, "event_created", summary=summary)
        await state.clear()
        if hasattr(message, "edit_text"):
            await message.edit_text(text, parse_mode="HTML")
        else:
            await message.answer(text, parse_mode="HTML")
    finally:
        await conn.close()


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


# --- Edit event handlers ---


@router.callback_query(F.data.startswith("ev:edit:"))
async def cb_event_edit(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    event_id = int(cb.data.split(":")[2])
    conn = await get_db()
    try:
        event = await get_event_by_id(conn, event_id)
        if not event:
            lang = "ru" if (cb.from_user.language_code or "").startswith("ru") else "en"
            await cb.answer(t(lang, "event_deleted"), show_alert=True)
            return
        user_db_id = await get_or_create_user(conn, cb.from_user.id)
        if event.user_id != user_db_id:
            await cb.answer("Нет доступа." if (cb.from_user.language_code or "").startswith("ru") else "No access.", show_alert=True)
            return
        lang, _ = await get_user_settings(conn, cb.from_user.id) or ("ru", DEFAULT_TIMEZONE)
        dt_str = format_utc_for_display(event.event_datetime, event.timezone)
        await state.set_state(EditEventStates.choose_field)
        await state.update_data(
            event_id=event_id,
            lang=lang,
            event_title=event.title,
            event_datetime_str=dt_str,
        )
        await cb.message.edit_text(
            t(lang, "edit_what"),
            reply_markup=edit_field_kb(lang, event_id),
        )
    finally:
        await conn.close()


@router.callback_query(F.data.startswith("edit:field:"))
async def cb_edit_field(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    parts = cb.data.split(":")
    if len(parts) < 4:
        return
    field, event_id_str = parts[2], parts[3]
    event_id = int(event_id_str)
    data = await state.get_data()
    lang = data.get("lang", "ru")

    if field == "cancel":
        await state.clear()
        try:
            await cb.message.edit_text(t(lang, "cancelled"))
        except Exception:
            await cb.message.answer(t(lang, "cancelled"))
        return

    conn = await get_db()
    try:
        event = await get_event_by_id(conn, event_id)
        if not event:
            await state.clear()
            await cb.message.edit_text(t(lang, "event_deleted"))
            return
        user_db_id = await get_or_create_user(conn, cb.from_user.id)
        if event.user_id != user_db_id:
            await cb.answer("Нет доступа." if lang == "ru" else "No access.", show_alert=True)
            return

        await state.update_data(event_id=event_id)

        if field == "title":
            await state.set_state(EditEventStates.edit_title)
            hint = t(lang, "edit_current_title", title=event.title)
            await cb.message.edit_text(
                t(lang, "ask_event_title") + "\n\n" + hint,
                reply_markup=cancel_kb(lang),
            )
        elif field == "datetime":
            await state.set_state(EditEventStates.edit_datetime)
            dt_str = format_utc_for_display(event.event_datetime, event.timezone)
            hint = t(lang, "edit_current_datetime", datetime=dt_str)
            await cb.message.edit_text(
                t(lang, "ask_event_datetime") + "\n\n" + hint,
                reply_markup=datetime_calendar_kb(lang),
            )
        elif field == "recurrence":
            await state.set_state(EditEventStates.edit_recurrence)
            await cb.message.edit_text(
                t(lang, "ask_recurrence"),
                reply_markup=edit_recurrence_kb(lang, event_id),
            )
    finally:
        await conn.close()


@router.callback_query(F.data.startswith("edit:rec:"))
async def cb_edit_recurrence(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    parts = cb.data.split(":")
    if len(parts) < 4:
        return
    rec_type, event_id_str = parts[2], parts[3]
    event_id = int(event_id_str)
    data = await state.get_data()
    lang = data.get("lang", "ru")

    conn = await get_db()
    try:
        event = await get_event_by_id(conn, event_id)
        if not event:
            await state.clear()
            await cb.message.edit_text(t(lang, "event_deleted"))
            return
        user_db_id = await get_or_create_user(conn, cb.from_user.id)
        if event.user_id != user_db_id:
            await cb.answer("Нет доступа.", show_alert=True)
            return

        if rec_type == "once":
            await update_event(conn, event_id, recurrence_type=RECURRENCE_NONE, recurrence_value="")
            await _finish_edit(cb, state, lang)
        elif rec_type == "weekly":
            await state.set_state(EditEventStates.edit_weekly_day)
            await state.update_data(event_id=event_id)
            await cb.message.edit_text(t(lang, "ask_weekly_day"), reply_markup=edit_weekly_days_kb(lang, event_id))
        elif rec_type == "monthly":
            await state.set_state(EditEventStates.edit_monthly_day)
            await state.update_data(event_id=event_id)
            await cb.message.edit_text(t(lang, "ask_monthly_day"), reply_markup=cancel_kb(lang))
    finally:
        await conn.close()


@router.callback_query(F.data.startswith("edit:day:"))
async def cb_edit_weekly_day(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    parts = cb.data.split(":")
    if len(parts) < 4:
        return
    day, event_id_str = parts[2], parts[3]
    event_id = int(event_id_str)
    data = await state.get_data()
    lang = data.get("lang", "ru")

    conn = await get_db()
    try:
        await update_event(conn, event_id, recurrence_type=RECURRENCE_WEEKLY, recurrence_value=day)
        await _finish_edit(cb, state, lang)
    finally:
        await conn.close()


@router.message(EditEventStates.edit_title, F.text)
async def process_edit_title(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    event_id = data.get("event_id")
    if not event_id or not message.text or len(message.text.strip()) < 2:
        await message.answer("Введи название (минимум 2 символа)." if lang == "ru" else "Enter title (min 2 chars).")
        return
    conn = await get_db()
    try:
        event = await get_event_by_id(conn, event_id)
        if event and event.user_id == await get_or_create_user(conn, message.from_user.id):
            await update_event(conn, event_id, title=message.text.strip())
            await state.clear()
            await message.answer(t(lang, "event_updated"))
        else:
            await state.clear()
            await message.answer(t(lang, "event_deleted"))
    finally:
        await conn.close()


@router.message(EditEventStates.edit_datetime, F.text)
async def process_edit_datetime(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    event_id = data.get("event_id")
    dt = _parse_datetime(message.text or "")
    if not dt:
        await message.answer(t(lang, "invalid_datetime"))
        return
    conn = await get_db()
    try:
        event = await get_event_by_id(conn, event_id)
        if not event or event.user_id != await get_or_create_user(conn, message.from_user.id):
            await state.clear()
            await message.answer(t(lang, "event_deleted"))
            return
        dt_utc = local_to_utc(dt, event.timezone)
        if dt_utc < utc_now():
            await message.answer(t(lang, "datetime_past"))
            return
        await update_event(conn, event_id, event_datetime=dt_utc)
        await state.clear()
        await message.answer(t(lang, "event_updated"))
    finally:
        await conn.close()


@router.message(EditEventStates.edit_datetime_time, F.text)
async def process_edit_datetime_time(message: Message, state: FSMContext):
    """Parse time after calendar date selection when editing."""
    data = await state.get_data()
    lang = data.get("lang", "ru")
    event_id = data.get("event_id")
    calendar_date = data.get("calendar_date")
    if not calendar_date:
        await state.clear()
        await message.answer(t(lang, "event_deleted"))
        return
    parsed = _parse_time(message.text or "")
    if not parsed:
        await message.answer("Введи время в формате ЧЧ:ММ" if lang == "ru" else "Enter time as HH:MM")
        return
    hour, minute = parsed
    dt = datetime(calendar_date.year, calendar_date.month, calendar_date.day, hour, minute)
    conn = await get_db()
    try:
        event = await get_event_by_id(conn, event_id)
        if not event or event.user_id != await get_or_create_user(conn, message.from_user.id):
            await state.clear()
            await message.answer(t(lang, "event_deleted"))
            return
        dt_utc = local_to_utc(dt, event.timezone)
        if dt_utc < utc_now():
            await message.answer(t(lang, "datetime_past"))
            return
        await update_event(conn, event_id, event_datetime=dt_utc)
        await state.clear()
        await message.answer(t(lang, "event_updated"))
    finally:
        await conn.close()


@router.message(EditEventStates.edit_monthly_day, F.text)
async def process_edit_monthly_day(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    event_id = data.get("event_id")
    try:
        day = int(message.text.strip())
        if 1 <= day <= 31:
            conn = await get_db()
            try:
                event = await get_event_by_id(conn, event_id)
                if event and event.user_id == await get_or_create_user(conn, message.from_user.id):
                    await update_event(conn, event_id, recurrence_type=RECURRENCE_MONTHLY, recurrence_value=str(day))
                    await state.clear()
                    await message.answer(t(lang, "event_updated"))
                else:
                    await state.clear()
                    await message.answer(t(lang, "event_deleted"))
            finally:
                await conn.close()
        else:
            await message.answer(t(lang, "invalid_day"))
    except ValueError:
        await message.answer(t(lang, "invalid_day"))


async def _finish_edit(cb: CallbackQuery, state: FSMContext, lang: str):
    await state.clear()
    try:
        await cb.message.edit_text(cb.message.text + "\n\n✅ " + t(lang, "event_updated"))
    except Exception:
        await cb.message.answer(t(lang, "event_updated"))


@router.callback_query(F.data == "cancel")
async def cancel_add(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    data = await state.get_data()
    lang = data.get("lang", "ru") if data else "ru"
    await state.clear()
    try:
        await cb.message.edit_text(t(lang, "cancelled"))
    except Exception:
        await cb.message.answer(t(lang, "cancelled"))
