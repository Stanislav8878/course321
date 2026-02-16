# Habit Tracker Backend
## Стек

- Python 3.10+
- Django, Django REST Framework
- PostgreSQL
- Redis
- Celery + Celery Beat
- Telegram Bot API
- JWT (djangorestframework-simplejwt)
- drf-spectacular (Swagger / OpenAPI)
- django-cors-headers

---

## Быстрый старт через Docker Compose

### 1) Подготовьте переменные окружения

В корне проекта есть шаблон: `.env.example`.

Скопируйте его в `.env` и при необходимости поменяйте значения:

```bash
cp .env.example .env
```

Минимально важно заменить:
- `SECRET_KEY`
- `TELEGRAM_BOT_TOKEN` (если используете Telegram-уведомления)

> В шаблоне уже указаны правильные хосты для docker-compose: `DB_HOST=db`, `redis://redis:6379/...`.

### 2) Запуск одной командой

```bash
docker compose up --build -d
```

### 3) Проверка работоспособности сервисов

**Backend (Django)**
- Swagger: http://localhost:8000/api/docs/
- OpenAPI schema: http://localhost:8000/api/schema/

Проверка по логам:
```bash
docker compose logs -f backend
```

**PostgreSQL**
```bash
docker compose exec db psql -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;"
```

**Redis**
```bash
docker compose exec redis redis-cli ping
# ожидается: PONG
```

**Celery worker**
```bash
docker compose logs -f celery
```

**Celery Beat (планировщик)**
```bash
docker compose logs -f celery-beat
```

### Остановка

```bash
docker compose down
```

Если хотите удалить том с базой данных:
```bash
docker compose down -v
```

---

## Локальный запуск без Docker (опционально)

См. зависимости в `requirements.txt`.

1. Создать и активировать виртуальное окружение
2. Установить зависимости `pip install -r requirements.txt`
3. Создать `.env` (можно на основе `.env.example`)
4. Применить миграции `python manage.py migrate`
5. Запустить сервер `python manage.py runserver`

---

## Основные эндпоинты

- `POST /api/users/register/` — регистрация
- `POST /api/users/login/` — получение JWT
- `GET /api/habits/` — список привычек пользователя
- `POST /api/habits/` — создание привычки
- `GET /api/habits/{id}/` — просмотр привычки
- `PUT/PATCH /api/habits/{id}/` — редактирование привычки
- `DELETE /api/habits/{id}/` — удаление привычки
- `GET /api/habits/public/` — список публичных привычек
- `POST /api/telegram/save-chat-id/` — сохранить chat_id Telegram для текущего пользователя
- `GET /api/docs/` — Swagger UI
- `GET /api/schema/` — OpenAPI схема

---

## Тесты и качество кода

Запуск тестов с покрытием:

```bash
coverage run -m pytest
coverage report
```

Запуск Flake8:

```bash
flake8
```
