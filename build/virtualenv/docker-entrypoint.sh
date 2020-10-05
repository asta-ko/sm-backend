#!/bin/sh
set -e

#while ! nc -z $DB_HOST $DB_PORT; do
#    echo "Postgres is unavailable - sleeping"
#    sleep 1;
#done

echo "Postgres is up - continuing"

# Apply database migrations
if [ "x$DJANGO_MANAGE_MIGRATE" = 'xon' ]; then
    echo "Apply database migrations"
    python -m oi_sud migrate --noinput
fi

# Collect static files
if [ "x$DJANGO_MANAGE_COLLECTSTATIC" = 'xon' ]; then
    echo "Collect static files"
    python -m oi_sud collectstatic --noinput
fi

exec "$@"
