---
title: About
permalink: /about/
---

# About

Singularity Registry Server is an open source registry for Singularity
containers. To read more about it's background, see {% include doc.html name="the introduction" path="introduction" %}.
For policy, including license, and suggested usage agreement, see [the policy page]({{ site.baseurl }}/policy).

## What infrastructure is needed?

Singularity Registry Server needs a web accessible server that can install and run Docker and Docker Compose. I (@vsoch) originally started developing it within a Singularity container, but decided to user Docker. Why?

 1. Feedback was strongly that Docker would be ok for such an application. More institutions are able to support separate servers for applications like this.
 2. Docker is great and optimized for orchestration of services. Singularity is not close to that, and with the default image type being an (unchangeable) squashfs, it does not seem to be moving in a direction to be optimized for service containers.
 3. Since images are pushed and pulled via `PUT` and `POST`, it isn't the case that the registry needs to be part of the cluster itself. We don't have the same security concerns as we do with running containers.

The components of the application include databases, a web server, worker, and application:

 - **quay.io/vanessa/sregistry**: is the main uwsgi application, which serves a Django (python-based) application.
 - **nginx**: pronounced (engine-X) is the webserver. The starter application is configured for http, however you should follow the instructions to set up https properly. Note that we build a custom nginx image that takes advantage of the [nginx upload module](https://www.nginx.com/resources/wiki/modules/upload/).
 - **worker**: is the same uwsgi image, but with a running command that is specialized to perform tasks. The tasks are run via [django-rq](https://github.com/rq/django-rq) that uses a
 - **redis**: database to organize the jobs themselves.
 - **scheduler** jobs can be scheduled using the scheduler.

This means that, given a pretty basic server to run the application, and enough space connected to it to store the images, you can bring the entire thing up relatively quickly. Awesome! Let's get started and talk about first steps of [install]({{ site.baseurl }}/docs/install). Or read about [use cases first]({{ site.baseurl }}/docs/use-cases)

## Support

If you need help, please don't hesitate to [open an issue](https://www.github.com/{{ site.github_repo }}/{{ site.github_user }}).
