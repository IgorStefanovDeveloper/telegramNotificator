"""Inline keyboards for the bot."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from i18n import t
from database.models import RECURRENCE_NONE, RECURRENCE_MONTHLY, RECURRENCE_WEEKLY


def main_menu(lang: str) -> ReplyKeyboardMarkup:
    """Main menu with reply keyboard."""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text=t(lang, "btn_new_event")),
        KeyboardButton(text=t(lang, "btn_list_events")),
    )
    builder.row(KeyboardButton(text=t(lang, "btn_settings")))
    return builder.as_markup(resize_keyboard=True)


def recurrence_kb(lang: str) -> InlineKeyboardMarkup:
    """Choose recurrence: once, weekly, monthly."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t(lang, "btn_once"), callback_data="rec:once"),
        InlineKeyboardButton(text=t(lang, "btn_weekly"), callback_data="rec:weekly"),
        InlineKeyboardButton(text=t(lang, "btn_monthly"), callback_data="rec:monthly"),
    )
    return builder.as_markup()


def weekly_days_kb(lang: str) -> InlineKeyboardMarkup:
    """Choose weekday. 0=Mon, 6=Sun."""
    builder = InlineKeyboardBuilder()
    row1 = [
        InlineKeyboardButton(text=t(lang, "mon"), callback_data="day:0"),
        InlineKeyboardButton(text=t(lang, "tue"), callback_data="day:1"),
        InlineKeyboardButton(text=t(lang, "wed"), callback_data="day:2"),
        InlineKeyboardButton(text=t(lang, "thu"), callback_data="day:3"),
    ]
    row2 = [
        InlineKeyboardButton(text=t(lang, "fri"), callback_data="day:4"),
        InlineKeyboardButton(text=t(lang, "sat"), callback_data="day:5"),
        InlineKeyboardButton(text=t(lang, "sun"), callback_data="day:6"),
    ]
    builder.row(*row1)
    builder.row(*row2)
    return builder.as_markup()


def event_actions_kb(event_id: int, lang: str) -> InlineKeyboardMarkup:
    """Done / Postpone / Edit / Delete for event."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t(lang, "btn_done"), callback_data=f"ev:done:{event_id}"),
        InlineKeyboardButton(text=t(lang, "btn_postpone"), callback_data=f"ev:postpone:{event_id}"),
    )
    builder.row(
        InlineKeyboardButton(text=t(lang, "btn_edit"), callback_data=f"ev:edit:{event_id}"),
        InlineKeyboardButton(text=t(lang, "btn_delete"), callback_data=f"ev:del:{event_id}"),
    )
    return builder.as_markup()


def notification_actions_kb(event_id: int, lang: str) -> InlineKeyboardMarkup:
    """Done / Postpone / Edit for notification."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t(lang, "btn_done"), callback_data=f"ev:done:{event_id}"),
        InlineKeyboardButton(text=t(lang, "btn_postpone"), callback_data=f"ev:postpone:{event_id}"),
        InlineKeyboardButton(text=t(lang, "btn_edit"), callback_data=f"ev:edit:{event_id}"),
    )
    return builder.as_markup()


def edit_field_kb(lang: str, event_id: int) -> InlineKeyboardMarkup:
    """Choose which field to edit: title, datetime, recurrence."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t(lang, "btn_edit_title"), callback_data=f"edit:field:title:{event_id}"),
        InlineKeyboardButton(text=t(lang, "btn_edit_datetime"), callback_data=f"edit:field:datetime:{event_id}"),
    )
    builder.row(
        InlineKeyboardButton(text=t(lang, "btn_edit_recurrence"), callback_data=f"edit:field:recurrence:{event_id}"),
        InlineKeyboardButton(text=t(lang, "cancel"), callback_data=f"edit:field:cancel:{event_id}"),
    )
    return builder.as_markup()


def edit_recurrence_kb(lang: str, event_id: int) -> InlineKeyboardMarkup:
    """Recurrence options for edit."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t(lang, "btn_once"), callback_data=f"edit:rec:once:{event_id}"),
        InlineKeyboardButton(text=t(lang, "btn_weekly"), callback_data=f"edit:rec:weekly:{event_id}"),
        InlineKeyboardButton(text=t(lang, "btn_monthly"), callback_data=f"edit:rec:monthly:{event_id}"),
    )
    builder.row(InlineKeyboardButton(text=t(lang, "cancel"), callback_data=f"edit:field:cancel:{event_id}"))
    return builder.as_markup()


def edit_weekly_days_kb(lang: str, event_id: int) -> InlineKeyboardMarkup:
    """Weekday selection for edit."""
    builder = InlineKeyboardBuilder()
    row1 = [
        InlineKeyboardButton(text=t(lang, "mon"), callback_data=f"edit:day:0:{event_id}"),
        InlineKeyboardButton(text=t(lang, "tue"), callback_data=f"edit:day:1:{event_id}"),
        InlineKeyboardButton(text=t(lang, "wed"), callback_data=f"edit:day:2:{event_id}"),
        InlineKeyboardButton(text=t(lang, "thu"), callback_data=f"edit:day:3:{event_id}"),
    ]
    row2 = [
        InlineKeyboardButton(text=t(lang, "fri"), callback_data=f"edit:day:4:{event_id}"),
        InlineKeyboardButton(text=t(lang, "sat"), callback_data=f"edit:day:5:{event_id}"),
        InlineKeyboardButton(text=t(lang, "sun"), callback_data=f"edit:day:6:{event_id}"),
    ]
    builder.row(*row1)
    builder.row(*row2)
    builder.row(InlineKeyboardButton(text=t(lang, "cancel"), callback_data=f"edit:field:cancel:{event_id}"))
    return builder.as_markup()


def list_events_kb(events: list, lang: str) -> InlineKeyboardMarkup:
    """Edit/Delete buttons for each event in the list. events: list of Event-like objects with .id."""
    builder = InlineKeyboardBuilder()
    for ev in events:
        builder.row(
            InlineKeyboardButton(text=t(lang, "btn_edit"), callback_data=f"ev:edit:{ev.id}"),
            InlineKeyboardButton(text=t(lang, "btn_delete"), callback_data=f"ev:del:{ev.id}"),
        )
    return builder.as_markup()


def settings_kb(lang: str) -> InlineKeyboardMarkup:
    """Language selection."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t(lang, "btn_lang_ru"), callback_data="set:lang:ru"),
        InlineKeyboardButton(text=t(lang, "btn_lang_en"), callback_data="set:lang:en"),
    )
    return builder.as_markup()


def cancel_kb(lang: str) -> InlineKeyboardMarkup:
    """Cancel button."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=t(lang, "cancel"), callback_data="cancel"))
    return builder.as_markup()


def datetime_calendar_kb(lang: str) -> InlineKeyboardMarkup:
    """Calendar and Cancel buttons for date selection."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t(lang, "btn_calendar"), callback_data="cal:open"),
        InlineKeyboardButton(text=t(lang, "cancel"), callback_data="cancel"),
    )
    return builder.as_markup()
