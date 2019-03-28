---
layout: default
title: "pam-auth - Authentication with PAM"
pdf: true
permalink: /plugin-pam
toc: false
---

The `pam_auth` plugin allows users to login to sregistry using the unix accounts on 
the host syste.

To enable PAM authentication you must:

  * Uncomment the Dockerfile section to install PAM dependencies *before* building the image
  * Add `pam_auth` to the `PLUGINS_ENABLED` list in `shub/settings/config.py`

The rules with respect to user collections still hold true - each user is given
push access given that they are added to a team, or `USER_COLLECTIONS` is true.
The users will still each need to export their token to push.  You can read [more about roles here](https://singularityhub.github.io/sregistry/setup-roles), and [more about teams](https://singularityhub.github.io/sregistry/setup-teams) to manage groups of people.

The user that runs the web server (in the case of Docker, root) needs to be 
a member of the /etc/shadow file. We add this to lines in the Dockerfile that you
must uncomment (step 1) in order for the plugin to be enabled:

```bash
# Install PAM Authentication (uncomment if wanted)
RUN pip install django-pam && \
    USER=$(whoami) && \
    usermod -a -G shadow "${USER}"
```

Finally, if you decide to mount the shadow and users file from your host,
you need to edit the `docker-compose.yml` and uncomment binds to your host:

```bash
uwsgi:
  restart: always
  image: vanessa/sregistry
  volumes:
    - .:/code
    - ./static:/var/www/static
    - ./images:/var/www/images
    # uncomment for PAM auth if you want the host users
    #- /etc/passwd:/etc/passwd 
    #- /etc/shadow:/etc/shadow
  links:
    - redis
    - db
```

Note that this solution [would require restarting the container](https://github.com/jupyterhub/jupyterhub/issues/535) for changes on the host to take effect. If you find
a better way to do this, please test and open an issue to add to this documentation.

## Testing Pam

Once you bring up the image with `docker-compose up -d`, you can test PAM
by shelling inside and adding a new user:

```bash
$ CONTAINER_ID=$(docker ps -q --filter="NAME=sregistry_uwsgi_1")
$ docker exec -it $CONTAINER_ID bash
```

Once in the container, add a user:

```bash
$ useradd vanessa -p pancakes
```

Then outside the container, restart.

```bash
$ docker-compose restart
```

<div>
    <a href="/sregistry/plugin-ldap"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry/plugin-globus"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
