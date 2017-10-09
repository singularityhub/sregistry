# Singularity Registry

[![status](http://joss.theoj.org/papers/050362b7e7691d2a5d0ebed8251bc01e/status.svg)](http://joss.theoj.org/papers/050362b7e7691d2a5d0ebed8251bc01e)

- [Documentation](https://singularityhub.github.io/sregistry)

## What is Singularity Registry
Singularity Registry is a management and storage of Singularity images for an institution or user to deploy locally. It does not manage building, but serves endpoints to obtain and save containers. The Registry is expected to be available for use in the Fall.

## Images Included
Singularity Registry consists of several Docker images, and they are integrated to work together using [docker-compose.yml](docker-compose.yml). The images are the following:

 - **vanessa/sregistry**: is the main uwsgi application, which serves a Django (python-based) application.
 - **nginx**: pronounced (engine-X) is the webserver. The starter application is configured for http, however you should follow the instructions to set up https properly.
 - **worker**: is the same uwsgi image, but with a running command that is specialized to perform tasks. The tasks are run via [celery](http://www.celeryproject.org/), a distributed job queue that fits nicely into Django. The celery worker uses a
 - **redis**: database to organize the jobs themselves.

For more information about Singularity Registry, please reference the [docs](https://singularityhub.github.io/sregistry). If you have any issues, please [let me know](https://github.com/singularityhub/sregistry/issues)!
