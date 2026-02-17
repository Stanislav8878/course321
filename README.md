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

