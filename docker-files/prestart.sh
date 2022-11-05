#! /usr/bin/env sh

# create migrations (TODO: This should be controlled by an env variable)
echo "${0}: making migrations."
django-admin makemigrations --noinput

echo "${0}: running migrations."
python /app/manage.py migrate --noinput

echo "${0}: collecting statics."
python /app/manage.py collectstatic --noinput
