#!/bin/sh
set -e

# Move tables from the old app names (clrSite, libraryApp) first; safe to run every deploy.
python manage.py rename_legacy_apps
python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn castle_project.wsgi:application --bind 0.0.0.0:${PORT:-8080} --workers ${WEB_CONCURRENCY:-2} --timeout 120 --access-logfile - --error-logfile -
