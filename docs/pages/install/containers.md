---
layout: default
title: "Installation: Containers"
pdf: true
permalink: /install-containers
toc: true
---

# Installation: Start Containers

Whether you build or not, the compose command will bring up the application (and download `vanessa/sregistry` image if not found in your cache).

```bash
docker-compose up -d
```

The `-d` means detached, and that you won't see any output (or errors) to the console. You can easily restart and stop containers, either specifying the container name(s) or leaving blank to apply to all containers. Note that these commands must be run in the folder with the `docker-compose.yml`:

```bash
docker-compose restart uwsgi worker nginx
docker-compose stop
```

When you do `docker-compose up -d` the application should be available at `http://127.0.0.1/`, and if you've configured https, `https://127.0.0.1/`. If you need to shell into the application, for example to debug with `python manage.py shell` you can get the container id with `docker ps` and then do:

```bash
NAME=$(docker ps -aqf "name=sregistry_uwsgi_1")
docker exec -it ${NAME} bash
```

If you make changes to the image itself, you will need to build again. However, if you just make changes to some static code, since it's mounted at `/code`, you can generally just restart:

```bash
docker-compose restart
```

Good job! Now it's time to read the [setup](/sregistry/setup) guide to better understand how to configure and interact with your Singularity Registry.
