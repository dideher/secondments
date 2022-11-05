#! /usr/bin/env sh

echo "${0}: running migrations."
python /app/manage.py migrate --noinput

echo "${0}: collecting statics."
python /app/manage.py collectstatic --noinput
