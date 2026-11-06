#!/bin/sh
set -e

# Move tables from the old app names (clrSite, libraryApp) first; safe to run every deploy.
python manage.py rename_legacy_apps
python manage.py migrate --noinput

# Sevalla's build already runs collectstatic (STATIC_ROOT is set), so the server can start
# straight away. Only collect here if the build did not produce the manifest.
if [ ! -f staticfiles/staticfiles.json ]; then
    python manage.py collectstatic --noinput
fi

exec gunicorn castle_project.wsgi:application --bind 0.0.0.0:${PORT:-8080} --workers ${WEB_CONCURRENCY:-2} --timeout 120 --access-logfile - --error-logfile -
