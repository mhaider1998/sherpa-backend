#!/bin/sh

set -e

export DB_NAME="devdb"
export DB_USER="devuser"
export DB_PASS="devdbpass"
export DJANGO_SECRET_KEY="changeme"
export DJANGO_ALLOWED_HOSTS="127.0.0.1"

python manage.py wait_for_db
python manage.py collectstatic --noinput
python manage.py migrate

uwsgi --socket :9000 --workers 4 --master --master --enable-threads --module app.wsgi