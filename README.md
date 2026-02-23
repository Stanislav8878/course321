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


---

## Деплой на удалённый сервер (Docker + Nginx) — вариант для задания

Ниже — **проверяемая** схема деплоя: GitHub Actions → сборка Docker-образа → push в **GitHub Container Registry (GHCR)** → SSH на сервер → `docker compose pull && up -d`.

### 0) Что будет на сервере

- Docker Engine + Docker Compose plugin
- Открыт только **22/tcp** (SSH) и **80/tcp** (HTTP) (при необходимости 443/tcp)
- Проект лежит, например, в: `/opt/habit-tracker`
- В этой папке на сервере есть:
  - `docker-compose.prod.yml` (из репозитория)
  - `deploy/nginx.conf` (из репозитория)
  - `.env` (создаёте на сервере по шаблону `.env.example`, **в git не коммитится**)

### 1) Подготовка сервера (Ubuntu/Debian)

#### 1.1 Создайте пользователя и включите SSH-ключи

На локальной машине:
```bash
ssh-keygen -t ed25519 -C "github-actions"
```

На сервере:
```bash
sudo adduser deploy
sudo usermod -aG sudo deploy
sudo mkdir -p /home/deploy/.ssh
sudo nano /home/deploy/.ssh/authorized_keys   # вставьте публичный ключ
sudo chmod 700 /home/deploy/.ssh
sudo chmod 600 /home/deploy/.ssh/authorized_keys
sudo chown -R deploy:deploy /home/deploy/.ssh
```

Рекомендуется отключить парольный вход:
- `/etc/ssh/sshd_config`: `PasswordAuthentication no`, `PermitRootLogin no`
- затем:
```bash
sudo systemctl reload ssh
```

#### 1.2 Установите Docker

Установите Docker по официальной инструкции для вашей ОС.

Проверьте:
```bash
docker --version
docker compose version
```

Добавьте пользователя в группу docker:
```bash
sudo usermod -aG docker deploy
# перелогиньтесь
```

#### 1.3 Настройте firewall (UFW)

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
# sudo ufw allow 443/tcp   # если нужен https
sudo ufw enable
sudo ufw status
```

### 2) Размещение файлов проекта на сервере (один раз)

```bash
sudo mkdir -p /opt/habit-tracker
sudo chown -R deploy:deploy /opt/habit-tracker
```

Скопируйте на сервер (один раз) `docker-compose.prod.yml` и папку `deploy/`:
```bash
scp docker-compose.prod.yml deploy/nginx.conf deploy@<SERVER_IP>:/opt/habit-tracker/ -r
```

Создайте `.env` на сервере:
```bash
cd /opt/habit-tracker
cp .env.example .env   # если вы копируете файл туда вручную
nano .env
```

Важно:
- `APP_IMAGE=...` можно поставить любым значением — GitHub Actions будет обновлять его при деплое.
- не коммитьте `.env` в git.

Запуск вручную (проверка):
```bash
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml ps
```

Приложение будет доступно по IP/домену сервера на **80 порту**.

---

## CI/CD: GitHub Actions (тесты + деплой)

Workflow лежит в репозитории: **`.github/workflows/ci_cd.yml`**

### Как работает

- На **каждый push** запускается job `test`:
  - поднимает `postgres` и `redis` как services
  - ставит зависимости
  - делает `migrate`
  - запускает `pytest`
  - если тесты упали — деплой не выполняется
- Job `deploy` запускается **только если**:
  - `test` прошёл успешно
  - это **push в ветку `develop`**
- В `deploy`:
  - собирается Docker-образ и пушится в **GHCR**
  - по SSH выполняются команды на сервере:
    - обновляется `APP_IMAGE` в `.env`
    - `docker compose pull && docker compose up -d`

### Какие Secrets нужно добавить в GitHub

Откройте репозиторий → **Settings → Secrets and variables → Actions → New repository secret**.

Добавьте:

- `SSH_HOST` — IP или домен сервера
- `SSH_USER` — пользователь на сервере (например `deploy`)
- `SSH_PORT` — обычно `22`
- `SSH_KEY` — приватный ключ (полностью, включая строки `-----BEGIN ...` и `-----END ...`)
- `SERVER_PATH` — путь к папке проекта на сервере, например `/opt/habit-tracker`

> `GITHUB_TOKEN` добавлять не нужно — GitHub создаёт его автоматически, workflow использует его для GHCR.

### Где смотреть отчёты по тестам/деплою

GitHub → вкладка **Actions** → нужный запуск → смотрите логи `test` и `deploy`.

---

## Частые ошибки проверки

1) **В репозиторий случайно попал `.env` или `.git/`**
- Убедитесь, что `.env` игнорируется и удалён из истории коммитов.
- В PR не должно быть `.env`, `.idea`, `venv`, `__pycache__` и т.п.

2) **Deploy не стартует**
- Он запускается только на `push` в `develop`. Для PR — только тесты.

3) **Неверный путь на сервере**
- Проверьте `SERVER_PATH` и что там есть `docker-compose.prod.yml` и `.env`.
---

## Адрес развернутого приложения

- API (nginx → gunicorn): **http://89.169.187.83/**
- Swagger (через nginx): **http://89.169.187.83/api/docs/**

> Если у вас настроен домен/HTTPS — укажите здесь домен вместо IP.

---

## Деплой на сервер через Docker Compose (production)

В репозитории есть production-конфигурация: `docker-compose.prod.yml` (Django+Gunicorn, PostgreSQL, Redis, Celery, Celery Beat, nginx).

### 1) Подготовка сервера (Ubuntu 22.04/24.04)

1. Обновите систему и установите Docker + Compose plugin:

```bash
sudo apt update
sudo apt -y install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo   "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu   $(. /etc/os-release && echo "$VERSION_CODENAME") stable" |   sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker
```

2. Откройте порт 80 (если включён ufw):

```bash
sudo ufw allow 80/tcp
sudo ufw enable
sudo ufw status
```

3. (Рекомендуется) Создайте директорию проекта на сервере:

```bash
sudo mkdir -p /opt/habit-tracker
sudo chown -R $USER:$USER /opt/habit-tracker
cd /opt/habit-tracker
```

### 2) Файлы на сервере

На сервере должны быть:
- `docker-compose.prod.yml` (можно копировать из репозитория)
- `.env` (секреты и настройки окружения)
- `deploy/nginx.conf` (конфиг nginx из репозитория)

Минимальный пример `.env`:
```env
DEBUG=0
SECRET_KEY=change-me

DB_NAME=habits
DB_USER=habits
DB_PASSWORD=habits
DB_HOST=db
DB_PORT=5432

REDIS_URL=redis://redis:6379/0

ALLOWED_HOSTS=89.169.187.83,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://89.169.187.83

# образ приложения, который будет собран и опубликован CI
APP_IMAGE=ghcr.io/<GITHUB_USERNAME>/<REPO_NAME>:latest
```

> Файл `.env` **не коммитим**. В репозитории хранится только `.env.example`.

### 3) Первый запуск на сервере (вручную)

```bash
cd /opt/habit-tracker
docker compose -f docker-compose.prod.yml --env-file .env up -d
docker compose -f docker-compose.prod.yml ps
```

Проверка логов:
```bash
docker compose -f docker-compose.prod.yml logs -f backend
```

Остановка/перезапуск:
```bash
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

---

## CI/CD (GitHub Actions)

CI/CD настроен так, чтобы при пуше/мерже в `develop`:

1) запустить линтер и тесты  
2) проверить сборку Docker-образа  
3) собрать и опубликовать Docker-образ в registry (например, GHCR)  
4) по SSH подключиться к серверу и выполнить обновление через Docker Compose

### Секреты GitHub (Settings → Secrets and variables → Actions)

Добавьте следующие Secrets:

- `SSH_HOST` — IP/домен сервера (например `89.169.187.83`)
- `SSH_USER` — пользователь для подключения (например `ronin909`)
- `SSH_PRIVATE_KEY` — приватный ключ (OpenSSH), соответствующий ключу в `~/.ssh/authorized_keys` на сервере
- `ENV_FILE` — содержимое `.env` для production (одним текстом)
- `GHCR_PAT` — токен GitHub с правами `write:packages` (если пушите образ в GHCR)

> Можно не хранить `.env` как файл на сервере вручную — workflow может писать его из `ENV_FILE`.

### Что делает деплой (логика)

На сервере деплой обычно сводится к командам:

```bash
cd /opt/habit-tracker

# обновить compose/nginx.conf при необходимости (git pull или scp)
# авторизация в registry (если нужно)
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d --remove-orphans
docker image prune -f
```

---

## Примечания по nginx / статики

- В production `backend` запускается через gunicorn и **не** публикует порт наружу (используется `expose`).
- `nginx` проксирует запросы на `backend:8000` и раздаёт статику из volume `static_data`.
- Сбор статики выполняется автоматически при старте `backend` благодаря переменной `RUN_MIGRATIONS=1` (см. `docker/entrypoint.sh`).

---

## Полезные команды

Миграции/создание суперпользователя в Docker:

```bash
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py showmigrations
```

Подключиться к Postgres:

```bash
docker compose exec db psql -U "$DB_USER" -d "$DB_NAME"
```
