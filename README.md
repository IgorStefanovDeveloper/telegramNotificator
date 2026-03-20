# Telegram Event Reminder Bot

Бот для напоминаний о событиях с поддержкой повторяющихся событий (еженедельно/ежемесячно).

## Возможности

- ✅ Добавление событий с датой и временем (МСК по умолчанию)
- ✅ Уведомления в момент наступления события (до 3 сообщений с интервалом 30 мин, если нет ответа)
- ✅ Действия в уведомлении: выполнено / отложить / изменить / отменить (мягкая отмена)
- ✅ Список грядущих (`/list` или кнопка «📅 Список событий»), выполненных и отменённых (кнопки «✅ Выполненные» / «🚫 Отменённые» или `/done`, `/cancelled`)
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
| `DATABASE_URL` | **PostgreSQL** (рекомендуется для Railway). Если задан — SQLite не используется. |
| `DATABASE_PATH` | Путь к SQLite, только если `DATABASE_URL` пуст (по умолчанию `./data/events.db`) |
| `DATABASE_SSL` | Для Postgres: `1` (по умолчанию, TLS) или `0` для локального Postgres без SSL |

## Данные

- **У каждого пользователя свои события** — изоляция по `telegram_id`, чужие события недоступны.
- **PostgreSQL** (продакшен на Railway): подключите плагин Postgres — в сервис бота подставится `DATABASE_URL`, данные не пропадают при редеплое.
- **SQLite** (локально): один файл `data/events.db`; при запуске только additive-миграции, без пересоздания таблиц.

## Деплой на бесплатный хостинг

### Railway
1. Зарегистрируйтесь на [railway.app](https://railway.app)
2. New Project → Deploy from GitHub (ваш репозиторий с ботом)
3. В проект добавьте **PostgreSQL** (New → Database → PostgreSQL)
4. В сервисе бота: **Variables** → **Add Reference** → выберите Postgres → подставьте `DATABASE_URL` (или Railway сделает это сам при линке сервисов)
5. Задайте `TELEGRAM_BOT_TOKEN`
6. Запуск: `python main.py` (или укажите в настройках сервиса)

**Альтернатива без Postgres:** [Volume](https://docs.railway.app/reference/volumes) на `/data` и `DATABASE_PATH=/data/events.db` — иначе SQLite в контейнере будет теряться при редеплое.

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

**PostgreSQL:** делайте дампы через `pg_dump` (из Railway Postgres или локально с тем же `DATABASE_URL`).

**SQLite:** один файл — просто скопируйте `data/events.db`.

**Переезд SQLite → Postgres:** автоматического импорта нет; для больших данных используйте скрипт или `pgloader`. Для пары пользователей можно заново создать события или выгрузить вручную.

## Безопасность

- Все секреты хранятся в `.env` (не коммитить!)
- Файл `.env` в `.gitignore`