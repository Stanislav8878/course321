#!/bin/sh
set -e

if [ $# -eq 0 ]; then
  set -- gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
fi

if [ "${RUN_MIGRATIONS}" = "1" ]; then
  echo "Running migrations..."
  python manage.py migrate --noinput
fi

if [ "${COLLECT_STATIC}" = "1" ]; then
  echo "Collecting static..."
  python manage.py collectstatic --noinput
fi

exec "$@"