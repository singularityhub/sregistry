---
title: "Plugin: Custom Builder and Storage"
pdf: true
toc: true
permalink: docs/plugins/remote-build
---

# Plugin: Remote Build mimic sylabs API

## Configure sregistry

By default, remote build is disabled. To configure sregistry to 
use Google Cloud build and Storage, in settings/config.py you can enable the plugin by 
uncommenting it from the list here:

```bash
PLUGINS_ENABLED = [
#    'ldap_auth',
#    'saml_auth',
#    'globus',
#     'google_build',
     'remote_build'
]
```
You will need to build the image locally with, at least, the build argument ENABLE_REMOTEBUILD set to true:

```bash
$ docker build --build-arg ENABLE_REMOTEBUILD=true -t quay.io/quay.io/vanessa/sregistry .
```

## Secrets

Next, set the following variables in `shub/settings/secrets.py`, 
that you can create from `dummy_secrets.py` in the shub/settings folder.
The first two speak for themselves, your project name and path to your
Google Application Credentials.

## Singularity Remote Build

This is a first effort to provide support to `remote build`.
Freshly build image on application server (aka `worker`) is then pushed on library...
So we need [singularity client](https://sylabs.io) installed on application server.

### Motivation

Remote build provide user without local compute resource (for instance), 
to build remotely and retrieved locally container image on their desktop.

It's also a way to share quickly conitainer image.

You can proceed through [googlebuild](https://singularityhub.github.io/sregistry/docs/plugins/google-build) plugin,
but it's not everyone that have the opportunity to access google cloud, for security reason for instance...

### In the nutshell

This basic implementation of the Sylabs Library API use django
[channels](https://channels.readthedocs.io/en/latest/) Websocket Server
[Daphne](https://github.com/django/daphne/) and [ASGI](https://channels.readthedocs.io/en/latest/asgi.html)

### Requisite

This is the same than for [Singularity Push](#singularity-push)

### Install

You need to build new locally image, with new argument ENABLE_REMOTEBUILD set to true:

```
docker build --build-arg ENABLE_REMOTEBUILD=true -t quay.io/quay.io/vanessa/sregistry .
```

### Utilisation

To build remotely image on [sregistry](https://singularityhub.github.io/sregistry):

```
singularity build --builder https://127.0.0.1 --remote <image name> <spec file>
```

Container image `<image name>` will then be generate locally and on remote library.

To generate image only remotely, use:

```
singularity build --builder https://127.0.0.1 --detached <spec file>
```

### Features

- [X] build on remote library
- [X] retrieve locally build
- [ ] implement `WYSIWYG` via web interface through popular [django-ace](https://github.com/django-ace/django-ace)

### TODO :boom:

- [ ] Automatically create collection `remote-builds`
- [ ] Re-use Django Push View in Build View
- [ ] Optimize channels consumer `BuildConsumer`
- [ ] Extend collection spacename to username
- [ ] Dedicated worker for build

