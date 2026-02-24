#!/bin/sh
set -e

if [ "$1" = "celery" ]; then
  exec celery -A config worker -l info
fi

if [ "$1" = "celery-beat" ]; then
  exec celery -A config beat -l info
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000