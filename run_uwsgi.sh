#!/bin/bash

python manage.py makemigrations users
python manage.py makemigrations api
python manage.py makemigrations logs
python manage.py makemigrations main
python manage.py makemigrations
python manage.py migrate users
python manage.py migrate auth
python manage.py migrate
python manage.py collectstatic --noinput
service cron start

if python manage.py show_settings PLUGINS_ENABLED | grep -q globus
then
    # When configured, we can start the endpoint
    echo "Starting Globus Connect Personal"
    export USER="tunel-user"
    /opt/globus/globusconnectpersonal -start &
fi

# Make sure directories that are shared are created
mkdir -p /var/www/images/_upload/{0..9} && chmod 777 -R /var/www/images/_upload

uwsgi uwsgi.ini
