#!/bin/sh

python manage.py flush --noinput
python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn --bind 0.0.0.0:$DJANGO_INTERNAL_PORT $DJANGO_WSGI_MODULE:application
