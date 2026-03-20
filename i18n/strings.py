"""Translations for Russian and English."""

TEXTS = {
    "ru": {
        "welcome": "Привет! 👋 Я бот для напоминаний о событиях.\n\n"
                   "• Добавляй события с датой и временем\n"
                   "• До 3 напоминаний по событию (повторы через 30 мин)\n"
                   "• Повторы: еженедельно или ежемесячно\n"
                   "• /list — грядущие, /done — выполненные, /cancelled — отменённые\n\n"
                   "Нажми /help для команд.",
        "help": "📋 <b>Команды</b>\n\n"
                "/new — добавить событие\n"
                "/list — грядущие события\n"
                "/done — выполненные\n"
                "/cancelled — отменённые\n"
                "/settings — язык и часовой пояс\n\n"
                "До 3 напоминаний по событию: вовремя и два повтора через 30 мин, если нет ответа.",
        "menu_main": "Главное меню",
        "btn_new_event": "➕ Новое событие",
        "btn_list_events": "📅 Список событий",
        "btn_settings": "⚙️ Настройки",
        "ask_event_title": "Введи название события:",
        "ask_event_date": "Выбери дату:",
        "ask_event_datetime": "Введи дату и время в формате <code>ДД.ММ.ГГГГ ЧЧ:ММ</code>\n"
                              "или выбери дату в календаре:\n\n"
                              "Например: 19.03.2025 14:30",
        "btn_calendar": "📅 Календарь",
        "ask_event_time": "Выбери время или введи вручную (ЧЧ:ММ):",
        "btn_time_manual": "✏️ Ввести вручную",
        "ask_recurrence": "Повторять событие?",
        "btn_once": "Один раз",
        "btn_weekly": "Еженедельно",
        "btn_monthly": "Ежемесячно",
        "ask_weekly_day": "Выбери день недели:",
        "mon": "Пн", "tue": "Вт", "wed": "Ср", "thu": "Чт", "fri": "Пт", "sat": "Сб", "sun": "Вс",
        "ask_monthly_day": "Введи число месяца (1–31):",
        "event_created": "✅ Событие создано!\n\n{summary}",
        "event_summary": "📌 {title}\n🕐 {datetime}\n{recurrence}",
        "recurrence_once": "Повтор: один раз",
        "recurrence_weekly": "Повтор: каждый {day}",
        "recurrence_monthly": "Повтор: каждый месяц, {day}-е число",
        "list_upcoming": "📅 <b>Грядущие события</b> (до 2 лет):\n\n{events}",
        "list_empty": "Нет запланированных событий.\n\nДобавь новое: /new",
        "event_item": "• {title} — {datetime}\n  {recurrence_line}",
        "event_item_recurring_weekly": "• Каждый {day} — {title} — {datetime}",
        "event_item_recurring_monthly": "• Каждое {day} число месяца — {title} — {datetime}",
        "event_actions": "Действия с событием",
        "btn_done": "✅ Выполнено",
        "btn_postpone": "⏰ Отложить на час",
        "btn_edit": "✏️ Редактировать",
        "btn_delete": "🗑 Удалить",
        "event_done": "Отлично! Событие отмечено выполненным.",
        "event_postponed": "Событие отложено на час.",
        "event_deleted": "Событие удалено.",
        "event_cancelled": "Событие отменено.",
        "btn_cancel_event": "🚫 Отменить",
        "notification_nudge": "🔔 <b>Напоминание</b> (ещё раз)\n\n{title}\n🕐 {datetime}",
        "list_completed": "✅ <b>Выполненные</b> (последние):\n\n{events}",
        "list_cancelled": "🚫 <b>Отменённые</b> (последние):\n\n{events}",
        "list_history_empty": "Здесь пока пусто.",
        "notification": "🔔 <b>Напоминание</b>\n\n{title}\n🕐 {datetime}",
        "settings": "⚙️ <b>Настройки</b>\n\nЯзык: {language}\nЧасовой пояс: {timezone}",
        "btn_lang_ru": "🇷🇺 Русский",
        "btn_lang_en": "🇬🇧 English",
        "lang_changed": "Язык изменён.",
        "timezone_changed": "Часовой пояс изменён.",
        "invalid_datetime": "Неверный формат. Используй ДД.ММ.ГГГГ ЧЧ:ММ",
        "datetime_past": "Дата и время уже прошли. Введи будущую дату.",
        "invalid_day": "Введи число от 1 до 31.",
        "cancel": "Отмена",
        "cancelled": "Отменено.",
        "edit_what": "Что изменить?",
        "btn_edit_title": "Название",
        "btn_edit_datetime": "Дата и время",
        "btn_edit_recurrence": "Повтор",
        "event_updated": "Событие обновлено.",
        "edit_current_title": "Текущее: {title}",
        "edit_current_datetime": "Текущее: {datetime}",
    },
    "en": {
        "welcome": "Hi! 👋 I'm a reminder bot for events.\n\n"
                   "• Add events with date and time\n"
                   "• Up to 3 reminders per event (nudges every 30 min)\n"
                   "• Weekly or monthly repeats\n"
                   "• /list — upcoming, /done — completed, /cancelled — cancelled\n\n"
                   "Press /help for commands.",
        "help": "📋 <b>Commands</b>\n\n"
                "/new — add event\n"
                "/list — upcoming events\n"
                "/done — completed\n"
                "/cancelled — cancelled\n"
                "/settings — language and timezone\n\n"
                "Up to 3 reminders per event: on time plus two nudges 30 min apart if no response.",
        "menu_main": "Main menu",
        "btn_new_event": "➕ New event",
        "btn_list_events": "📅 List events",
        "btn_settings": "⚙️ Settings",
        "ask_event_title": "Enter event title:",
        "ask_event_date": "Select date:",
        "ask_event_datetime": "Enter date and time as <code>DD.MM.YYYY HH:MM</code>\n"
                              "or pick a date from the calendar:\n\n"
                              "Example: 19.03.2025 14:30",
        "btn_calendar": "📅 Calendar",
        "ask_event_time": "Select time or enter manually (HH:MM):",
        "btn_time_manual": "✏️ Enter manually",
        "ask_recurrence": "Repeat this event?",
        "btn_once": "Once",
        "btn_weekly": "Weekly",
        "btn_monthly": "Monthly",
        "ask_weekly_day": "Select day of week:",
        "mon": "Mon", "tue": "Tue", "wed": "Wed", "thu": "Thu", "fri": "Fri", "sat": "Sat", "sun": "Sun",
        "ask_monthly_day": "Enter day of month (1–31):",
        "event_created": "✅ Event created!\n\n{summary}",
        "event_summary": "📌 {title}\n🕐 {datetime}\n{recurrence}",
        "recurrence_once": "Repeat: once",
        "recurrence_weekly": "Repeat: every {day}",
        "recurrence_monthly": "Repeat: monthly on day {day}",
        "list_upcoming": "📅 <b>Upcoming events</b> (up to 2 years):\n\n{events}",
        "list_empty": "No scheduled events.\n\nAdd new: /new",
        "event_item": "• {title} — {datetime}\n  {recurrence_line}",
        "event_item_recurring_weekly": "• Every {day} — {title} — {datetime}",
        "event_item_recurring_monthly": "• Every {day} of the month — {title} — {datetime}",
        "event_actions": "Event actions",
        "btn_done": "✅ Done",
        "btn_postpone": "⏰ Postpone 1 hour",
        "btn_edit": "✏️ Edit",
        "btn_delete": "🗑 Delete",
        "event_done": "Done! Event marked as completed.",
        "event_postponed": "Event postponed by 1 hour.",
        "event_deleted": "Event deleted.",
        "event_cancelled": "Event cancelled.",
        "btn_cancel_event": "🚫 Cancel",
        "notification_nudge": "🔔 <b>Reminder</b> (again)\n\n{title}\n🕐 {datetime}",
        "list_completed": "✅ <b>Completed</b> (latest):\n\n{events}",
        "list_cancelled": "🚫 <b>Cancelled</b> (latest):\n\n{events}",
        "list_history_empty": "Nothing here yet.",
        "notification": "🔔 <b>Reminder</b>\n\n{title}\n🕐 {datetime}",
        "settings": "⚙️ <b>Settings</b>\n\nLanguage: {language}\nTimezone: {timezone}",
        "btn_lang_ru": "🇷🇺 Русский",
        "btn_lang_en": "🇬🇧 English",
        "lang_changed": "Language changed.",
        "timezone_changed": "Timezone changed.",
        "invalid_datetime": "Invalid format. Use DD.MM.YYYY HH:MM",
        "datetime_past": "Date and time are in the past. Enter a future date.",
        "invalid_day": "Enter a number from 1 to 31.",
        "cancel": "Cancel",
        "cancelled": "Cancelled.",
        "edit_what": "What to change?",
        "btn_edit_title": "Title",
        "btn_edit_datetime": "Date and time",
        "btn_edit_recurrence": "Repeat",
        "event_updated": "Event updated.",
        "edit_current_title": "Current: {title}",
        "edit_current_datetime": "Current: {datetime}",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    """Get translated string. Falls back to Russian."""
    text = TEXTS.get(lang, TEXTS["ru"]).get(key, TEXTS["ru"].get(key, key))
    return text.format(**kwargs) if kwargs else text


def get_all_texts(lang: str) -> dict:
    return TEXTS.get(lang, TEXTS["ru"])
