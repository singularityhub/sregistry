# Introduction
Singularity Registry is a Dockerized web application that an institution or individual can deploy to organize and manage Singularity images. Let's get familiar first with some of the basics.


## How are images named?
When you deploy your registry, you will give it a short identifier, such as `tacc`. This means that, for example, if you had a container called `science/rocks` with tag `latest`, and if you wanted to pull it using the Singularity software, the command would be:

```
singularity pull shub://tacc/science/rocks:latest
```

meaning that the complete uri is `shub://tacc/science/rocks:latest`. it's completely up to you how you want to manage your naming of images. Here are a few suggestions:

 - `[ cluster ]/[ project ]`
 - `[ group ]/[ project ]`
 - `[ user ]/[ project ]`

Singularity Hub, based on its connection with Github, uses `[ username ]/[ reponame ]`. If you manage repositories equivalently, you might also consider this as an idea. The one constaint on naming is that only the special character `-` is allowed, and all letters are automatically made lowercase. There are fewer bugs that way, trust us.

## How are images shared?
The reason that `tacc` is understood by the Singularity software is because it has been registered with Singularity Hub. If your registry has public images, we encourage you to register it officially with Singularity Hub, so that other users can easily pull your images, directed from Singularity Hub. If you don't register, you can still use the local registry, but specify your own url to it. For example:

```
singularity pull shub://127.0.0.1/science/rocks:latest # localhost
singularity pull shub://tacc/science/rocks:latest      # registered with Singularity Hub, 
```

We recommend the second, because it's much nicer looking! :) Given that you have registered `tacc` with Singularity Hub, the address to query for the image download will be known.

## Container Lingo
Let's now talk about some commonly used terms.

### registry
The registry refers to this entire application. When you set up your registry, you will fill out some basic information in settings, and send it to Singularity Hub.

### collections
Each container image (eg, `shub://fishman/snacks`) is actually a set of images called a `collection`. Within a collection you might have different tags or versions for images. For example:

 - `fishman/snacks:latest`
 - `fishman/snacks:v2.1`
 - `fishman/snacks:cheetos`

All of these images are derivations of `fishman/snacks`, and so we find them in the same collection.

## What infrastructure is needed?
Singularity Registry needs a web accessible server that can install and run Docker and Docker Compose. I (@vsoch) originally started developing it within a Singularity container, but decided to user Docker. Why?

 1. Feedback was strongly that Docker would be ok for such an application. More institutions are able to support separate servers for applications like this.
 2. Docker is great and optimized for orchestration of services. Singularity is not close to that, and with the default image type being an (unchangeable) squashfs, it does not seem to be moving in a direction to be optimized for service containers.
 3. Since images are pushed and pulled via `PUT` and `POST`, it isn't the case that the registry needs to be part of the cluster itself. We don't have the same security concerns as we do with running containers.

As was stated in the base [README.md](./README.md) The components of the application include databases, a web server, worker, and application:

 - **vanessa/sregistry**: is the main uwsgi application, which serves a Django (python-based) application.
 - **nginx**: pronounced (engine-X) is the webserver. The starter application is configured for http, however you should follow the instructions to set up https properly.
 - **worker**: is the same uwsgi image, but with a running command that is specialized to perform tasks. The tasks are run via [celery](http://www.celeryproject.org/), a distributed job queue that fits nicely into Django. The celery worker uses a
 - **redis**: database to organize the jobs themselves.

This means that, given a pretty basic server to run the application, and enough space connected to it to store the images, you can bring the entire thing up relatively quickly. Awesome! Let's get started and talk about first steps of [deployment](deployment.md).
