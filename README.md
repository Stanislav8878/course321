# Habit Tracker Backend

Курсовой проект: бэкенд SPA-приложения для отслеживания привычек.

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

## Требования

См. `requirements.txt`:

```bash
pip install -r requirements.txt
Настройка
Склонировать репозиторий:

bash
Копировать код
git clone https://github.com/USERNAME/habit-tracker-backend.git
cd habit-tracker-backend
Создать и активировать виртуальное окружение:

bash
Копировать код
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
Установить зависимости:

bash
Копировать код
pip install -r requirements.txt
Создать файл .env:

env
Копировать код
DEBUG=True
SECRET_KEY=your_secret_key
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=habits_db
DB_USER=habits_user
DB_PASSWORD=strong_password
DB_HOST=127.0.0.1
DB_PORT=5432

TELEGRAM_BOT_TOKEN=123456:ABCDEF
TELEGRAM_API_URL=https://api.telegram.org

REDIS_URL=redis://127.0.0.1:6379/0
CELERY_BROKER_URL=redis://127.0.0.1:6379/1
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/2
Применить миграции:

bash
Копировать код
python manage.py migrate
Создать суперпользователя:

bash
Копировать код
python manage.py createsuperuser
Запустить сервер разработки:

bash
Копировать код
python manage.py runserver
Запустить Redis, Celery и Celery Beat:

bash
Копировать код
redis-server
celery -A config worker -l INFO
celery -A config beat -l INFO
Эндпоинты
POST /api/users/register/ — регистрация

POST /api/users/token/ — получение JWT (логин)

POST /api/users/token/refresh/ — обновление JWT

GET /api/habits/ — список привычек текущего пользователя (с пагинацией)

POST /api/habits/ — создание привычки

GET /api/habits/{id}/ — просмотр привычки

PUT/PATCH /api/habits/{id}/ — редактирование привычки

DELETE /api/habits/{id}/ — удаление привычки

GET /api/habits/public/ — список публичных привычек

POST /api/telegram/save-chat-id/ — сохранить chat_id Telegram для текущего пользователя

GET /api/docs/ — Swagger UI

GET /api/schema/ — OpenAPI схема

Тесты и качество кода
Запуск тестов с покрытием:

bash
Копировать код
coverage run -m pytest
coverage report
Запуск Flake8:

bash
Копировать код
flake8