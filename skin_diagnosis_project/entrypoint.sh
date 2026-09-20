#!/bin/sh
set -e

# Wait for DB optionally (simple loop)
if [ -n "$DATABASE_URL" ]; then
  echo "DATABASE_URL is set"
fi

echo "Applying database migrations..."
python skin_diagnosis_backend/manage.py migrate --noinput

echo "Collecting static files..."
python skin_diagnosis_backend/manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn skin_diagnosis_backend.wsgi:application --bind 0.0.0.0:8000 --workers 3
