!/bin/bash

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

if grep -Fxq "PLUGINS_ENABLED+=[\"globus\"]" /code/shub/settings/config.py
then
    # When configured, we can start the endpoint
    echo "Starting Globus Connect Personal"
    export USER="tunel-user"
    /opt/globus/globusconnectpersonal -start &
fi

# Make sure directories that are shared are created
mkdir -p /var/www/images/_upload/{0..9} && chmod 777 -R /var/www/images/_upload

# to decode singularity spec file send by client POST
# as it's Go Marshal have been used, we need to call 
# Go Unmarshal in Python! 
[ -d /code/lib ] || mkdir -p /code/lib
[ -d /code/lib ] && 
    (cd /code/lib; [ -f unmarshal.go -a -x /usr/local/go/bin/go ] && 
    /usr/local/go/bin/go build -o unmarshal.so -buildmode=c-shared unmarshal.go)

# grep -Fxq seems not working...
[ $(awk 'BEGIN{ok=0}/PLUGINS_ENABLED/,/]/{if (!/#/&&/remote_build/) ok=1}END{print ok}' \
/code/shub/settings/config.py) -eq 0 ] && uwsgi uwsgi.ini ||
# Add support to websocket server, Daphne, throught django channels 
uwsgi uwsgi.ini & \
    daphne --root-path "/v1/build-ws" -b 0.0.0.0 -p 3032 --proxy-headers shub.plugins.remote_build.asgi:application
