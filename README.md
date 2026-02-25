# Habit Tracker (DRF + Celery + Telegram)

Сервис для ведения привычек и отправки напоминаний в Telegram.

## Адрес развернутого приложения

Сервер (Yandex Cloud VM): `http://130.193.53.177/` *(IP динамический — при пересоздании ВМ может измениться).* 

Документация (Swagger UI): `http://130.193.53.177/api/docs/`

## Функциональность

- Регистрация и авторизация по JWT.
- CRUD привычек **только для владельца**.
- Список публичных привычек (read-only).
- Пагинация: 5 привычек на страницу.
- Интеграция с Telegram: сохранение `chat_id` и рассылка напоминаний.
- Контейнеризация: Django, PostgreSQL, Redis, Celery worker, Celery beat, Nginx.
- CI/CD: GitHub Actions (lint + tests + docker build + deploy).

## API эндпоинты

### Пользователи

- `POST /api/users/register/` — регистрация
- `POST /api/users/token/` — получение JWT
- `POST /api/users/token/refresh/` — refresh

### Telegram

- `POST /api/telegram/save-chat-id/` — сохранить `chat_id` текущему пользователю

Тело запроса:

```json
{ "chat_id": "123456789" }
```

### Привычки

- `GET /api/habits/` — список привычек текущего пользователя (пагинация)
- `POST /api/habits/` — создание привычки
- `GET /api/habits/{id}/` — получить привычку
- `PATCH /api/habits/{id}/` — редактирование
- `DELETE /api/habits/{id}/` — удаление
- `GET /api/habits/public/` — список публичных привычек (read-only)

## Правила/валидаторы (ТЗ)

- Нельзя одновременно указать `reward` и `related_habit`.
- `duration` (в секундах) ≤ 120.
- `related_habit` может указывать только на привычку с `is_pleasant=true`.
- У приятной привычки (`is_pleasant=true`) не может быть `reward` и `related_habit`.
- `periodicity` в днях: от 1 до 7.

## Локальный запуск (Docker)

1) Скопируйте переменные окружения:

```bash
cp .env.example .env
```

2) Укажите `TELEGRAM_BOT_TOKEN` (получается у `@BotFather`).

3) Запустите проект:

```bash
docker compose up -d --build
```

4) Откройте документацию:

- `http://localhost/api/docs/`

> Nginx слушает порт 80, поэтому адрес без `:8000`.

## Как получить chat_id пользователя

1) Запустите вашего бота.
2) Напишите ему любое сообщение.
3) Узнайте `chat_id` (самый простой способ — временно включить вывод обновлений или использовать @userinfobot).
4) Вызовите эндпоинт:

```bash
curl -X POST http://localhost/api/telegram/save-chat-id/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"chat_id":"123456789"}'
```

## Напоминания (Celery)

- `celery_beat` запускает задачу `habits.tasks.send_habit_reminders` **каждую минуту**.
- Задача отправляет напоминание, когда текущая минута совпадает с `Habit.time`, и после последней отправки прошло не меньше `periodicity` дней.

## CORS

Управляется переменной `CORS_ALLOWED_ORIGINS`, пример в `.env.example`.

## CI/CD (GitHub Actions)

Workflow: `.github/workflows/ci-cd.yml`

### Секреты репозитория

В `Settings → Secrets and variables → Actions` добавьте:

- `DEPLOY_HOST` — IP сервера (например, `130.193.53.177`)
- `DEPLOY_USER` — пользователь (например, `ronin909`)
- `DEPLOY_SSH_KEY` — приватный SSH ключ (ed25519)
- `DEPLOY_PATH` — путь на сервере (например, `/home/ronin909/course321`)
- `ENV_FILE` — содержимое `.env` целиком (многострочным секретом)

### Что делает пайплайн

1) На PR/Push в `develop`:
   - flake8
   - pytest
   - проверка сборки docker образов

2) На push в `develop` (если проверки прошли):
   - подключается по SSH
   - обновляет код (`git pull`)
   - перезапускает сервис через `docker compose -f docker-compose.prod.yml up -d --build`

## Деплой на сервер вручную

На сервере должны быть установлены Docker и Docker Compose.

```bash
ssh -l ronin909 130.193.53.177
```

Далее:

```bash
git clone <repo> ~/course321
cd ~/course321
cp .env.example .env
docker compose -f docker-compose.prod.yml up -d --build
```
