---
layout: default
title: "Installation: Host"
pdf: true
permalink: /install-host
toc: false
---

# Installation
If starting from scratch, you need the following dependencies on the host:

 - [Docker](https://docs.docker.com/install/): a container engine
 - [docker-compose](https://docs.docker.com/compose/install/): an orchestration tool for Docker images.
 - python: docker compose requires some additional python libraries, `ipaddress` and `oauth2client`

Very importantly, if you are just installing Docker *you will need to log in and out after adding your user to the Docker group*. 

For a record of the installation procedure that I used for a Google Cloud host, I've provided the [basic commands](https://github.com/singularityhub/sregistry/blob/master/scripts/prepare_instance.sh). This script was run manually for an instance. This was done on a fairly large fresh ubuntu:16.04 instance on Google Cloud. This setup is done only once, and requires logging in and out of the instance after installing Docker, but before bringing the instance up with `docker-compose`. A few important points:

- The `$INSTALL_BASE` is set by default to `/opt`. It is recommended to choose somewhere like `/opt` or `/share` that is accessible by all those who will maintain the installation. If you choose your home directory, you can expect that only you would see it. If it's for personal use, `$HOME` is fine.
- Anaconda3 is installed for python libraries needed for `docker-compose`. You can use whatever python you with (system installed or virtual environment)
- Make sure to add all users to the docker group that need to maintain the application, and log in and out before use.

For the rest of the install procedure, you should (if you haven't already) clone the repository:

```
git clone https://github.com/singularityhub/sregistry
cd sregistry
```

For the files linked below, you should find the correspoinding file in the Github repository that you cloned. If you are setting this up for the first time, it's recommended to try locally and then move onto your production resource.

Next, why don't you [configure settings](/sregistry/install-settings) to customize your installation.
