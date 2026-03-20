"""Translations for Russian and English."""

TEXTS = {
    "ru": {
        "welcome": "Привет! 👋 Я бот для напоминаний о событиях.\n\n"
                   "• Добавляй события с датой и временем\n"
                   "• До 3 напоминаний по событию (повторы через 30 мин)\n"
                   "• Повторы: еженедельно или ежемесячно\n"
                   "• Под полем ввода — <b>5 кнопок</b> (в т.ч. «✅ Выполненные», «🚫 Отменённые»)\n"
                   "• Или меню <b>/</b> в поле ввода: /done, /cancelled\n\n"
                   "Если видишь только 3 кнопки — это старая клавиатура: нажми ещё раз /start после обновления бота.\n\n"
                   "/help — все команды.",
        "help": "📋 <b>Команды</b>\n\n"
                "/new — добавить событие\n"
                "/list — грядущие (кнопка «📅 Список событий»)\n"
                "/done — сделанные / выполненные (кнопка «✅ Выполненные»)\n"
                "/cancelled — отменённые (= «отклонённые» из напоминания; кнопка «🚫 Отменённые»)\n"
                "/settings — язык и часовой пояс\n\n"
                "<b>Кнопки под полем ввода</b> — нажми /start или /help, если их не видно.\n\n"
                "До 3 напоминаний по событию: вовремя и два повтора через 30 мин, если нет ответа.",
        "menu_main": "Главное меню",
        "btn_new_event": "➕ Новое событие",
        "btn_list_events": "📅 Список событий",
        "btn_completed_list": "✅ Выполненные",
        "btn_cancelled_list": "🚫 Отменённые",
        "btn_settings": "⚙️ Настройки",
        "ask_event_title": "Введи название события:",
        "ask_event_date": "Выбери дату:",
        "ask_event_datetime": "Введи дату и время в формате <code>ДД.ММ.ГГГГ ЧЧ:ММ</code>\n"
                              "или выбери дату в календаре:\n\n"
                              "Например: 19.03.2025 14:30",
        "btn_calendar": "📅 Календарь",
        "ask_event_time": "Выбери время или введи вручную (ЧЧ:ММ):",
        "tz_events_hint": "🕐 Дата и время — в <b>твоём</b> часовом поясе: {zone}. Поменять: ⚙️ Настройки.",
        "tz_events_hint_short": "🕐 Пояс: {zone}",
        "btn_time_manual": "✏️ Ввести вручную",
        "ask_recurrence": "Повторять событие?",
        "btn_once": "Один раз",
        "btn_weekly": "Еженедельно",
        "btn_monthly": "Ежемесячно",
        "ask_weekly_day": "Выбери день недели:",
        "mon": "Пн", "tue": "Вт", "wed": "Ср", "thu": "Чт", "fri": "Пт", "sat": "Сб", "sun": "Вс",
        "ask_monthly_day": "Введи число месяца (1–31):",
        "event_created": "✅ Событие создано!\n\n{summary}\n\n<i>{tz_note}</i>",
        "event_created_tz_note": "Время сохранено в поясе: {zone}.",
        "event_summary": "📌 {title}\n🕐 {datetime}\n{recurrence}",
        "recurrence_once": "Повтор: один раз",
        "recurrence_weekly": "Повтор: каждый {day}",
        "recurrence_monthly": "Повтор: каждый месяц, {day}-е число",
        "list_upcoming": "📅 <b>Грядущие события</b> (до 2 лет)\n<i>{tz_intro}</i>\n\n{events}",
        "list_tz_intro": "Время — в поясе каждого события (как при создании).",
        "list_empty": "Нет запланированных событий.\n\nДобавь новое: /new\n"
                      "Выполненные и отменённые — кнопки ниже или /done и /cancelled.",
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
        "notification_nudge": "🔔 <b>Напоминание</b> (ещё раз)\n\n{title}\n🕐 {datetime}\n<i>{zone_hint}</i>",
        "list_completed": "✅ <b>Выполненные</b> (последние):\n\n{events}",
        "list_cancelled": "🚫 <b>Отменённые</b> (последние):\n\n{events}",
        "list_history_empty": "Здесь пока пусто. Отменить событие можно из уведомления (кнопка «🚫 Отменить»).",
        "menu_restore_hint": "👇 Кнопки меню снова под полем ввода.",
        "notification": "🔔 <b>Напоминание</b>\n\n{title}\n🕐 {datetime}\n<i>{zone_hint}</i>",
        "notification_zone_hint": "Пояс: {zone}",
        "settings": "⚙️ <b>Настройки</b>\n\nЯзык: {language}\nЧасовой пояс: {timezone}\n\nВыбери пояс для <b>новых</b> событий (ниже). Уже созданные хранят свой пояс.",
        "btn_lang_ru": "🇷🇺 Русский",
        "btn_lang_en": "🇬🇧 English",
        "lang_changed": "Язык изменён. Кнопки меню обновлены.",
        "timezone_changed": "Часовой пояс изменён. Новые события будут в выбранном поясе.",
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
                   "• <b>5 buttons</b> below the input (including ✅ Completed, 🚫 Cancelled)\n"
                   "• Or type <b>/</b> for /done, /cancelled\n\n"
                   "If you only see 3 buttons, that's an old keyboard — send /start again after the bot was updated.\n\n"
                   "/help — all commands.",
        "help": "📋 <b>Commands</b>\n\n"
                "/new — add event\n"
                "/list — upcoming (button «📅 List events»)\n"
                "/done — completed (button «✅ Completed»)\n"
                "/cancelled — cancelled from notification (button «🚫 Cancelled»)\n"
                "/settings — language and timezone\n\n"
                "<b>Buttons below the input</b> — send /start or /help if you don’t see them.\n\n"
                "Up to 3 reminders per event: on time plus two nudges 30 min apart if no response.",
        "menu_main": "Main menu",
        "btn_new_event": "➕ New event",
        "btn_list_events": "📅 List events",
        "btn_completed_list": "✅ Completed",
        "btn_cancelled_list": "🚫 Cancelled",
        "btn_settings": "⚙️ Settings",
        "ask_event_title": "Enter event title:",
        "ask_event_date": "Select date:",
        "ask_event_datetime": "Enter date and time as <code>DD.MM.YYYY HH:MM</code>\n"
                              "or pick a date from the calendar:\n\n"
                              "Example: 19.03.2025 14:30",
        "btn_calendar": "📅 Calendar",
        "ask_event_time": "Select time or enter manually (HH:MM):",
        "tz_events_hint": "🕐 Date and time are in <b>your</b> timezone: {zone}. Change in ⚙️ Settings.",
        "tz_events_hint_short": "🕐 Zone: {zone}",
        "btn_time_manual": "✏️ Enter manually",
        "ask_recurrence": "Repeat this event?",
        "btn_once": "Once",
        "btn_weekly": "Weekly",
        "btn_monthly": "Monthly",
        "ask_weekly_day": "Select day of week:",
        "mon": "Mon", "tue": "Tue", "wed": "Wed", "thu": "Thu", "fri": "Fri", "sat": "Sat", "sun": "Sun",
        "ask_monthly_day": "Enter day of month (1–31):",
        "event_created": "✅ Event created!\n\n{summary}\n\n<i>{tz_note}</i>",
        "event_created_tz_note": "Time stored in timezone: {zone}.",
        "event_summary": "📌 {title}\n🕐 {datetime}\n{recurrence}",
        "recurrence_once": "Repeat: once",
        "recurrence_weekly": "Repeat: every {day}",
        "recurrence_monthly": "Repeat: monthly on day {day}",
        "list_upcoming": "📅 <b>Upcoming events</b> (up to 2 years)\n<i>{tz_intro}</i>\n\n{events}",
        "list_tz_intro": "Times are shown in each event’s timezone (as when created).",
        "list_empty": "No scheduled events.\n\nAdd new: /new\n"
                      "Completed & cancelled: buttons below or /done and /cancelled.",
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
        "notification_nudge": "🔔 <b>Reminder</b> (again)\n\n{title}\n🕐 {datetime}\n<i>{zone_hint}</i>",
        "list_completed": "✅ <b>Completed</b> (latest):\n\n{events}",
        "list_cancelled": "🚫 <b>Cancelled</b> (latest):\n\n{events}",
        "list_history_empty": "Nothing here yet. Cancel an event from the notification (🚫 Cancel).",
        "menu_restore_hint": "👇 Menu buttons are shown again below the input.",
        "notification": "🔔 <b>Reminder</b>\n\n{title}\n🕐 {datetime}\n<i>{zone_hint}</i>",
        "notification_zone_hint": "Zone: {zone}",
        "settings": "⚙️ <b>Settings</b>\n\nLanguage: {language}\nTimezone: {timezone}\n\nChoose timezone for <b>new</b> events. Existing events keep their own zone.",
        "btn_lang_ru": "🇷🇺 Русский",
        "btn_lang_en": "🇬🇧 English",
        "lang_changed": "Language changed. Menu buttons updated.",
        "timezone_changed": "Timezone updated. New events will use it.",
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
