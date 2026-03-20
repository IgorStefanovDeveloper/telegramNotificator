# Telegram Event Reminder Bot

Бот для напоминаний о событиях с поддержкой повторяющихся событий (еженедельно/ежемесячно).

## Возможности

- ✅ Добавление событий с датой и временем (МСК по умолчанию)
- ✅ Уведомления в момент наступления события (до 3 сообщений с интервалом 30 мин, если нет ответа)
- ✅ Действия в уведомлении: выполнено / отложить / изменить / отменить (мягкая отмена)
- ✅ Список грядущих (`/list`), выполненных (`/done`), отменённых (`/cancelled`)
- ✅ Повторяющиеся события: каждый понедельник, каждое 19-е число и т.п.
- ✅ Удаление и редактирование событий
- ✅ Русский и английский интерфейс

## Установка

```bash
# Клонировать и перейти в папку
cd telegramNotificator

# Виртуальное окружение (рекомендуется)
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac

# Зависимости
pip install -r requirements.txt

# Настроить секреты
copy .env.example .env
# Отредактировать .env и добавить TELEGRAM_BOT_TOKEN от @BotFather
```

## Запуск

```bash
python main.py
```

## Конфигурация (.env)

| Переменная | Описание |
|------------|----------|
| `TELEGRAM_BOT_TOKEN` | Токен бота от @BotFather (обязательно) |
| `DATABASE_PATH` | Путь к SQLite (по умолчанию `./data/events.db`) |

## Данные

- **У каждого пользователя свои события** — изоляция по `telegram_id`, чужие события недоступны.
- **БД — один файл SQLite** (`data/events.db`), удобно бэкапить и переносить.
- **Обновление схемы:** при запуске выполняются только additive-миграции (`ALTER TABLE ... ADD COLUMN`); данные не пересоздаются. Старый файл `events.db` подхватится автоматически.

## Деплой на бесплатный хостинг

### Railway
1. Зарегистрируйтесь на [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Добавьте переменную `TELEGRAM_BOT_TOKEN`
4. **Важно:** добавьте [Volume](https://docs.railway.app/reference/volumes), примонтируйте к `/data`, и задайте переменную `DATABASE_PATH=/data/events.db` — иначе БД будет сбрасываться при каждом редеплое.
5. Railway запустит `python main.py` автоматически

### Render
1. [render.com](https://render.com) → New → Background Worker
2. Подключите репозиторий
3. Build: `pip install -r requirements.txt`
4. Start: `python main.py`
5. Добавьте `TELEGRAM_BOT_TOKEN` в Environment

### PythonAnywhere
1. Создайте бесплатный аккаунт
2. Загрузите код через Git или Files
3. Создайте Always-On Task с командой `python main.py`

## Тесты

```bash
# Все тесты (unit + integration)
python -m pytest tests -v

# Только unit
python -m pytest tests -m "not integration" -v

# Только integration
python -m pytest tests -m integration -v
```

## Резервное копирование и миграция

SQLite хранит всё в одном файле — его можно просто скопировать.

**Скачать БД с Railway:**
```bash
# Через Railway CLI
railway run cp data/events.db ./events_backup.db
# Затем скачайте events_backup.db через dashboard или railway connect
```

**Или через One-off Command в Railway:** в Dashboard → ваш сервис → добавить временную команду `cat data/events.db | base64` и сохранить вывод (для небольшой БД).

**При переезде:** скопируйте `events.db` в папку `data/` на новом хосте и укажите `DATABASE_PATH=./data/events.db`. Структура таблиц совместима.

## Безопасность

- Все секреты хранятся в `.env` (не коммитить!)
- Файл `.env` в `.gitignore`