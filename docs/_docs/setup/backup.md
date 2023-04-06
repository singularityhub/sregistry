---
title: Deployment backup
description: Deployment backup
tags:
 - docker
---

# Backup

With changes to models and heavy development, there can be mistakes and errors
related to losing data. We can only do our best to back up the data locally,
back up the containers, and take snapshots of the server. This guide will provide
detail to that.

## Snapshots

If you are using Google Cloud, Google Cloud makes it easy to generate a snapshot schedule,
and then edit a Disk to associate it. Full instructions are [here](https://cloud.google.com/compute/docs/disks/scheduled-snapshots), and basically it comes down to:

 - Creating a snapshot schedule under Compute -> Snapshots. I typically chose daily, with snapshots expiring after 14 days
 - Editing the Disk under Compute -> Disks to use it.


## Containers

Since this is run directly on the server using Docker, it must be run with
the local cron. You can use crontab -e to edit the cron file, and crontab -l
to list and verify the edits. Specifically, you need to add this line:

```cron
0 1 * * * docker commit sregistry_uwsgi_1 quay.io/vanessa/sregistry:snapshot
0 1 * * * docker commit sregistry_db_1 quay.io/vanessa/sregistry-postgres:snapshot
0 1 * * * docker commit sregistry_redis_1 quay.io/vanessa/sregistry-redis:snapshot
0 1 * * * docker commit sregistry_scheduler_1 quay.io/vanessa/sregistry-scheduler:snapshot
0 1 * * * docker commit sregistry_worker_1 quay.io/vanessa/sregistry-worker:snapshot
```

This will run a docker commit at 1:00am, daily, using the container name
"sregistry_uwsgi_1" and saving to "quay.io/vanessa/sregistry:snapshot". When the snapshot
is saved for the disk (at 3-4am per the previous instructions) then
this container should be included. A few notes:

 - make sure that your containers are named as specified above - if you start from a different folder or use a different version of compose, you might see differences from the commands above.
 - You don't need to backup any database (db) container if you are using a non-container database.
 - The worker, scheduler, and base container are the same, so you can remove the last two lines if desired, and then if you need to restore, just tag the base image with the other names.

The above will commit the containers to your host, but of course doesn't help if you lose the host (hence why an additional
backup strategy for your host is recommended, as suggested above with the Google Cloud backup strategy).

## Database

For some hosts, I've found that the scheduled cron jobs to backup the container will work interactively, but not
successfully with cron. Thus, it's a better idea to run the database backup scripts from the host
via cron:

```
0 3 * * * docker exec sregistry_uwsgi_1 /code/scripts/backup_db.sh
```

It's also good practice to test running this script manually from inside the container,
along with running it via docker exec (outside of the cron job) after that. Finally,
once you've checked those two, you should also check the timestamp on the backup files
one day later to ensure that it ran on its own.
