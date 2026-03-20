# Telegram Event Reminder Bot

Бот для напоминаний о событиях с поддержкой повторяющихся событий (еженедельно/ежемесячно).

## Возможности

- ✅ Добавление событий с датой и временем; часовой пояс в ⚙️ Настройки: Москва или Нячанг/Вьетнам (UTC+7)
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
| `DATABASE_URL` | **PostgreSQL**, строка подключения (обязательно для бота) |
| `DATABASE_SSL` | Для Postgres: `1` (по умолчанию, TLS) или `0` для локального Postgres без SSL |
| `TEST_DATABASE_URL` | Отдельная БД для `pytest` (рекомендуется); иначе см. `tests/conftest.py` |

## Данные

- **У каждого пользователя свои события** — изоляция по `telegram_id`, чужие события недоступны.
- **PostgreSQL** обязателен: на Railway — плагин Postgres и `DATABASE_URL` в сервисе бота; локально — свой инстанс или Docker (см. ниже).

## Деплой на бесплатный хостинг

### Railway
1. Зарегистрируйтесь на [railway.app](https://railway.app)
2. New Project → Deploy from GitHub (ваш репозиторий с ботом)
3. В проект добавьте **PostgreSQL** (New → Database → PostgreSQL)
4. В сервисе бота: **Variables** → **Add Reference** → выберите Postgres → подставьте `DATABASE_URL` (или Railway сделает это сам при линке сервисов)
5. Задайте `TELEGRAM_BOT_TOKEN`
6. Запуск: `python main.py` (или укажите в настройках сервиса)

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

Нужен **PostgreSQL**. Удобно поднять контейнер:

```bash
docker run --name pg-bot-test -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=telegram_bot_test -p 5432:5432 -d postgres:16
```

По умолчанию тесты подключаются к `postgresql://postgres:postgres@127.0.0.1:5432/telegram_bot_test` и выставляют `DATABASE_SSL=0`. Свой URL: переменная **`TEST_DATABASE_URL`** (или **`DATABASE_URL`** до запуска pytest).

```bash
# Все тесты (unit + integration)
python -m pytest tests -v

# Только unit (всё равно нужен Postgres для test_events_repo)
python -m pytest tests -m "not integration" -v

# Только integration
python -m pytest tests -m integration -v
```

## Резервное копирование и миграция

**Резервные копии:** `pg_dump` с тем же `DATABASE_URL`, что у продакшена.

## Безопасность

- Все секреты хранятся в `.env` (не коммитить!)
- Файл `.env` в `.gitignore`