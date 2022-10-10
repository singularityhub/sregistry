---
title: "Plugin: Remote Builder and REST API endpoints"
pdf: false
toc: false
permalink: docs/plugins/remote-build
---

# Plugin: Remote Build mimic sylabs API

## Configure sregistry

By default, remote build is disabled. To configure Singularity Registry Server
to build remotely container image, in settings/config.py, you must enable this
plugin by uncommenting it from the list here:

```bash
PLUGINS_ENABLED = [
#    'ldap_auth',
#    'saml_auth',
#    'pam_auth',
#    'globus',
#     'google_build',
     'remote_build'
]
```
This plugin need a dedicated docker build image. So you will need to build
locally this image locally: 

```bash
$ docker build -f builder/Dockerfile -t quay.io/quay.io/vanessa/sregistry_builder .
$ cp builder/docker-compose.yml .
$ cp builder/nginx.conf.wss nging.conf # if use https
# cp builder/nginx.conf.wss nging.conf # or if use http

```

## Secrets

Next, set the following variables in `shub/settings/secrets.py`, 
that you can create from `dummy_secrets.py` in the shub/settings folder.
The first two speak for themselves, your project name and path to your
Google Application Credentials.

## Singularity Remote Build

This is a first effort to provide support to `remote build`.
Freshly build image on application builder is then pushed on library...
So we need [singularity client](https://sylabs.io) installed.

### Motivation

Remote build provide user without local compute resource (for instance), 
to build remotely and retrieved locally container image on their desktop.

Remote build activity can also be raised through API REST endpoint call.
Two endpoints have been added :  `/v1/push` and  `/v1/build`.
Indeed, build process can be split in two phases :

```bash
singularity build <image name> <spec file>  # Local resources consumption
singularity push <image name> library://<image uri> # Push to remote library
```

Both phases will be handled right now with only one command invocation:

```bash
singularity build --remote <image name> <spec file> # No consumption of local resources
```

Or soon (work still in progress):

```bash
http POST https://<library uri>/v1/build Authorization:"BEARER <TOKEN>"  \
Content-Disposition:"inline;filename=<image name>" @<image name>
```

`http` stand for popular [HTTP client](https://httpie.org/)

Work right now, `PUSH` endpoint:

```bash
curl -XPOST https://<library uri>/v1/push -H 'Authorization:BEARER <TOKEN>' \
--upload-file '<image name>' -H 'Content-Disposition:inline; filename=<image name>'
```

Using curl this time, but `httpie` work too...

Of cours, you can proceed through existing plugin : [google-build](https://singularityhub.github.io/sregistry/docs/plugins/google-build),
but it's not everyone who

have the opportunity to access google cloud, for security reason for instance...

### In the nutshell

This basic implementation of the Sylabs Library API use Django [channels](https://channels.readthedocs.io/en/latest/), 
Websocket Server [Daphne](https://github.com/django/daphne/) and [ASGI](https://channels.readthedocs.io/en/latest/asgi.html)

### Prerequisites

Apply the same requisites as is used for [Pushing Singularity image](https://singularityhub.github.io/sregistry/docs/client#singularity-push)

### Install

You need to build new locally image, with new argument ENABLE_REMOTEBUILD set to true:

```bash
$ docker build -f builder/Dockerfile -t quay.io/quay.io/vanessa/sregistry_builder .
$ cp builder/docker-compose.yml .
$ cp builder/nginx.conf.wss nging.conf # if use https
# cp builder/nginx.conf.wss nging.conf # or if use http
```

### Utilisation

To build remotely image on [sregistry](https://singularityhub.github.io/sregistry):

```bash
singularity build --builder https://<library uri> --remote <image name> <spec file>
```

Container image `<image name>` will then be generate locally and on remote library.

To generate image only remotely, use:

```bash
singularity build --builder https://<library uri> --detached <spec file>
```

### Features

- [X] build on remote library
- [X] retrieve locally build
- [ ] API REST endpoints to manipulate singularity images [WIP]

### TODO :boom:

- [X] Optimize channels consumer `BuildConsumer`
- [ ] Extend collection spacename to username
