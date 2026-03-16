"""Translations for Russian and English."""

TEXTS = {
    "ru": {
        "welcome": "Привет! 👋 Я бот для напоминаний о событиях.\n\n"
                   "• Добавляй события с датой и временем\n"
                   "• Получай уведомления вовремя\n"
                   "• События могут повторяться ежемесячно или еженедельно\n"
                   "• Просматривай грядущие события на 3 месяца вперёд\n\n"
                   "Нажми /help для списка команд.",
        "help": "📋 <b>Команды</b>\n\n"
                "/new — добавить событие\n"
                "/list — список грядущих событий\n"
                "/settings — язык и часовой пояс",
        "menu_main": "Главное меню",
        "btn_new_event": "➕ Новое событие",
        "btn_list_events": "📅 Список событий",
        "btn_settings": "⚙️ Настройки",
        "ask_event_title": "Введи название события:",
        "ask_event_datetime": "Введи дату и время в формате:\n"
                              "<code>ДД.ММ.ГГГГ ЧЧ:ММ</code>\n\n"
                              "Например: 19.03.2025 14:30",
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
        "list_upcoming": "📅 <b>Грядущие события</b> (на 3 месяца):\n\n{events}",
        "list_empty": "Нет запланированных событий.\n\nДобавь новое: /new",
        "event_item": "• {title} — {datetime}\n  {recurrence_line}",
        "event_actions": "Действия с событием",
        "btn_done": "✅ Выполнено",
        "btn_postpone": "⏰ Отложить на час",
        "btn_edit": "✏️ Редактировать",
        "btn_delete": "🗑 Удалить",
        "event_done": "Отлично! Событие отмечено выполненным.",
        "event_postponed": "Событие отложено на час.",
        "event_deleted": "Событие удалено.",
        "notification": "🔔 <b>Напоминание</b>\n\n{title}\n🕐 {datetime}",
        "settings": "⚙️ <b>Настройки</b>\n\nЯзык: {language}\nЧасовой пояс: {timezone}",
        "btn_lang_ru": "🇷🇺 Русский",
        "btn_lang_en": "🇬🇧 English",
        "lang_changed": "Язык изменён.",
        "timezone_changed": "Часовой пояс изменён.",
        "invalid_datetime": "Неверный формат. Используй ДД.ММ.ГГГГ ЧЧ:ММ",
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
                   "• Get notifications on time\n"
                   "• Events can repeat monthly or weekly\n"
                   "• View upcoming events for the next 3 months\n\n"
                   "Press /help for commands.",
        "help": "📋 <b>Commands</b>\n\n"
                "/new — add event\n"
                "/list — list upcoming events\n"
                "/settings — language and timezone",
        "menu_main": "Main menu",
        "btn_new_event": "➕ New event",
        "btn_list_events": "📅 List events",
        "btn_settings": "⚙️ Settings",
        "ask_event_title": "Enter event title:",
        "ask_event_datetime": "Enter date and time in format:\n"
                              "<code>DD.MM.YYYY HH:MM</code>\n\n"
                              "Example: 19.03.2025 14:30",
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
        "list_upcoming": "📅 <b>Upcoming events</b> (next 3 months):\n\n{events}",
        "list_empty": "No scheduled events.\n\nAdd new: /new",
        "event_item": "• {title} — {datetime}\n  {recurrence_line}",
        "event_actions": "Event actions",
        "btn_done": "✅ Done",
        "btn_postpone": "⏰ Postpone 1 hour",
        "btn_edit": "✏️ Edit",
        "btn_delete": "🗑 Delete",
        "event_done": "Done! Event marked as completed.",
        "event_postponed": "Event postponed by 1 hour.",
        "event_deleted": "Event deleted.",
        "notification": "🔔 <b>Reminder</b>\n\n{title}\n🕐 {datetime}",
        "settings": "⚙️ <b>Settings</b>\n\nLanguage: {language}\nTimezone: {timezone}",
        "btn_lang_ru": "🇷🇺 Русский",
        "btn_lang_en": "🇬🇧 English",
        "lang_changed": "Language changed.",
        "timezone_changed": "Timezone changed.",
        "invalid_datetime": "Invalid format. Use DD.MM.YYYY HH:MM",
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
