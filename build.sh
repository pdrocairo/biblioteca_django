#!/usr/bin/env bash
# Build do backend no Render: dependencias, estaticos e migrations.
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
