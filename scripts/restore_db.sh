#!/bin/bash

# **Important** run this command from inside the container, where you have
# Django and dependencies installed. This is typically run automatically 
# (nightly) via a cron job. See the Dockerfile, or shell into the uwsgi container:
# > service cron status
# > crontab -l
# > crontab -e

for db in "users" "api" "main" "logs" 
  do
    echo "Loading table $db"
    /usr/local/bin/python /code/manage.py loaddata /code/backup/$db.json
done
