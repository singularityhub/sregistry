# Backup

This README contains information about backing up containers and the database.

## Containers

If you use Singularity Registry Server with the default storing containers
on the filesystem, your containers will be preserved on the host in [images](../images).
This means that you can restore the registry with previous images, given that
this folder is on the host (bound at `/code/images` in the container).

## Database

This directory will be populated with a nightly backup, both for the previous
day and the one before that. It's run via a cron job that is scheduled in the
main uwsgi container:

```bash
RUN echo "0 1 * * * /bin/bash /code/scripts/backup_db.sh" >> /code/cronjob
```

It's a fairly simple strategy that will minimally allow you to restore your
registry database given that you accidentally remove and then recreate the db container.
For example, here we've started the containers, created some collections, uploaded
containers, and then we (manually) create a backup:

```bash
$ docker exec -it sregistry_uwsgi_1_210f9e7fc042 bash
$ /bin/bash /code/scripts/backup_db.sh
$ exit
```

Then stop and remove your containers.

```bash
$ docker-compose stop
$ docker-compose rm
```

Bring up the containers, and check the interface if you like to verify your
previous collection is gone. Again shell into the container,
but this time restore data.

```bash
$ docker exec -it sregistry_uwsgi_1_a5f868c10aa3 bash
$ /bin/bash /code/scripts/restore_db.sh
Loading table users
Installed 1 object(s) from 1 fixture(s)
Loading table api
Installed 1 object(s) from 1 fixture(s)
Loading table main
Installed 2 object(s) from 1 fixture(s)
Loading table logs
Installed 0 object(s) from 1 fixture(s)
```

If you browse to the interface, your collections should then be restored.
