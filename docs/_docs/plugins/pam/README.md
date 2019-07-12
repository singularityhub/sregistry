---
title: "pam-auth - Authentication with PAM"
pdf: true
toc: false
permalink: docs/plugins/pam
---

# PAM Authentication

The `pam_auth` plugin allows users to login to sregistry using the unix accounts on 
the host system.

To enable PAM authentication you must:

  * Uncomment the Dockerfile section to install PAM dependencies *before* building the image
  * Add `pam_auth` to the `PLUGINS_ENABLED` list in `shub/settings/config.py`
  * Uncomment binds to /etc/shadow and /etc/passwd in `docker-compose.yml`

More detailed instructions are below.

## Permissions

The rules with respect to user collections still hold true - each user is given
push access given that they are added to a team, or `USER_COLLECTIONS` is true,
and each user will still each need to export their token to push.  You can read [more about roles here](https://singularityhub.github.io/sregistry/setup-roles), and [more about teams](https://singularityhub.github.io/sregistry/setup-teams) to manage groups of people.


## Getting Started

This is the detailed walkthough to set up the PAM AUthentication plugin. 
First, uncomment installation of the module in the Dockerfile:

```bash
# Install PAM Authentication (uncomment if wanted)
RUN pip install django-pam
```

Then, uncomment "pam_auth" at the bottom of `shub/settings/config.py` to 
enable the login option.

```bash
PLUGINS_ENABLED = [
#    'ldap_auth',
    'pam_auth',
#    'globus',
#    'saml_auth'
]
```

Finally, since we need to get access to users from the host,
you need to edit the `docker-compose.yml` and uncomment binds to your host:

```bash
uwsgi:
  restart: always
  image: vanessa/sregistry
  volumes:
    - .:/code
    - ./static:/var/www/static
    - ./images:/var/www/images
    # uncomment for PAM auth
    #- /etc/passwd:/etc/passwd 
    #- /etc/shadow:/etc/shadow
  links:
    - redis
    - db
```

If you do this, we lose the user added in the container for nginx! 
You also need to add the nginx user to your host:

```bash
$ sudo addgroup --system nginx
$ sudo adduser --disabled-login --system --home /var/cache/nginx --ingroup nginx nginx
```

Note that this solution [would require restarting the container](https://github.com/jupyterhub/jupyterhub/issues/535) for changes on the host to take effect (for example,
adding new users). If you find a better way to do this, please test and open an issue to add to this documentation.
