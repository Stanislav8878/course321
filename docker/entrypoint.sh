#!/usr/bin/env sh
set -e

# Миграции и сбор статики делаем только для web-контейнера (backend),
# чтобы worker/beat не гоняли migrate/collectstatic на каждом старте.
if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
  python manage.py migrate --noinput
  python manage.py collectstatic --noinput
fi

exec "$@"