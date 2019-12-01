# Singularity Registry Server

[![status](http://joss.theoj.org/papers/050362b7e7691d2a5d0ebed8251bc01e/status.svg)](http://joss.theoj.org/papers/050362b7e7691d2a5d0ebed8251bc01e)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1012531.svg)](https://doi.org/10.5281/zenodo.1012531)

- [Documentation](https://singularityhub.github.io/sregistry)

## Contributors

![contributors.svg](./contributors.svg)

## What is Singularity Registry
Singularity Registry Server is a server to provide management and storage of 
Singularity images for an institution or user to deploy locally. 
It does not manage building, but serves endpoints to obtain and save containers. 

## Images Included
Singularity Registry consists of several Docker images, and they are integrated 
to work together using [docker-compose.yml](docker-compose.yml). 
The images are the following:

 - **vanessa/sregistry**: is the main uwsgi application, which serves a Django (python-based) application.
 - **nginx**: pronounced (engine-X) is the webserver. The starter application is configured for http, however you should follow the instructions to set up https properly. Note that we build a custom nginx image that takes advantage of the [nginx upload module](https://www.nginx.com/resources/wiki/modules/upload/).
 - **worker**: is the same uwsgi image, but with a running command that is specialized to perform tasks. The tasks are run via [django-rq](https://github.com/rq/django-rq) that uses a
 - **redis**: database to organize the jobs themselves.
 - **scheduler** jobs can be scheduled using the scheduler.

For more information about Singularity Registry Server, please reference the 
[docs](https://singularityhub.github.io/sregistry). If you have any issues, 
please [let me know](https://github.com/singularityhub/sregistry/issues)!

## License

This code is licensed under the MPL 2.0 [LICENSE](LICENSE).
