#!/bin/sh

set -e

echo "Waiting for Postgres at $POSTGRES_HOST:$POSTGRES_PORT..."

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 1
done

echo "Postgres started"

# Только для web делаем миграции
if [ "$1" = "gunicorn" ]; then
  echo "Apply migrations"
  python manage.py migrate

  echo "Collect static"
  python manage.py collectstatic --noinput
fi

exec "$@"