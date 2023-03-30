---
title: Frequently Asked Questions
pdf: true
toc: false
---

# Frequently Asked Questions

 - [What is Singularity Registry Server](#what-is-singularity-registry-server)
 - [What is a Linux Container?](#what-is-a-linux-container)
 - [How is Singularity Registry Server different from Singularity Hub?](#how-is-singularity-registry-server-different-from-singularity-hub)
 - [Why do we need Singularity containers?](#why-do-we-need-singularity-containers)
 - [Why isn't the storage backed up?](#why-isnt-the-storage-backed-up)
 - [How is a Singularity Registry different from a Docker Registry?](#how-is-a-singularity-registry-different-from-a-docker-registry)
 - [Are there features of Singularity that are particularly supported by Singularity Hub?](#are-there-features-of-singularity-that-are-particularly-supported-by-singularity-hub)


### What is Singularity Registry Server

Singularity Registry Server is an open source registry for [Singularity](https://www.github.com/sylabs/singularity)
containers. It is optimized to be flexible for deployment with different plugins for
authentication, storage, and building, and for community contribution.

### What is a Linux Container?

A container image is an encapsulated, portable environment that is created to distribute a scientific analysis or a general function. Containers help with reproducibility of such content as they nicely package software and data dependencies, along with libraries that are needed. Thus, the core of Singularity Hub are these Singularity container images, and by way of being on Singularity Hub they can be easily built, updated, referenced with a url for a publication, and shared. This small guide will help you to get started building your containers using Singularity Hub and your Github repositories.

### How is Singularity Hub related to Sylabs and Singularity?

[Sylabs](https://sylabs.io) is the company that maintains the open source [Singularity](https://www.github.com/sylabs/singularity) code base, along with providing services for paying customers that use Singularity containers. The creator and maintainer of Singularity Hub was one of the original Singularity (open source software) developers, however she is not affiliated with the company Sylabs. Singularity Hub continues to be maintained by this individual at Stanford University, with generous support from Google Cloud. The two now co-exist peacefully, both passionate about using and supporting users to build Singularity containers. The distinction between Sylabs Library and Singularity Hub (and [Singularity Registry Server](https://www.github.com/singularityhub/sregistry)) comes down to the intended communities that are served. Singularity Hub and Registry is a non-enterprise solution that is catered for research scientists.


### How is Singularity Registry Server different from Singularity Hub?

**Singularity Hub**

is the predecessor to Singularity Registry, and while it also serves as an image registry, in addition it provides a cloud build service for users. Singularity Hub also takes advantage of Github for version control of build recipes. The user pushes to Github, a builder is deployed, and the image available to the user. Singularity Hub would allow a user to build and run an image from a resource where he or she doesn't have sudo simply by using Github as a middleman.

**Singularity Registry Server**

is similarly an image registry that plugs in natively to the singularity software, but it places no dependencies on Github, and puts the power of deciding how to build in the hands of the user. This could mean building after tests pass with a "push" command in a Github repository, building via a SLURM job, or on a private server. While Singularity Hub is entirely public and only allows for a minimum number of private images, a Singularity Registry Server can be entirely private, with expiring tokens that can be shared. The administrator can choose
to include Singularity Hub like features via plugins, but only if they are desired.

Importantly, both deliver image manifests that plug seamlessly into the Singularity command-line software, so a registry (or hub) image can be pulled easily:

```bash
singularity pull shub://vsoch/hello-world
```

We are hoping to add builder plugins to Singularity Registry Server so that it can (eventually) replace Singularity Hub
as a truly community maintained, open source resource. Please contribute!


**Singularity Global Client**

`sregistry` is a general client for the single user to interact with containers at different endpoints. An endpoint could be a Singularity Registry Server, Singularity Hub, Google Drive/Cloud, Dropbox, or Globus.  You can think of it as a glue or fabric between all these different endpoints and APIs, as it allows you to create a local database to manage images. For this reason, the executable is called [sregistry](https://singularityhub.github.io/sregistry-cli).

### Why do we need Singularity containers?

Singularity containers allow you to package your entire scientific analysis, including dependencies, libraries, and environment, and run it anywhere. Inside a Singularity container you are the same user as outside the container, so you could not escalate to root and act maliciously on a shared resource. For more information on containers, see [the Singularity site](https://singularityware.github.io).


### Why isn't the storage backed up?

At the initial release of the software, because there are many different options for storage, enforcing a particular backup strategy would possibly make the registry less flexible to fit into many different use cases. In the same way that the institution is able to decide how to build, it is also under their decision for how to backup. For the database, django has different options for backup (for example [django-backup](https://github.com/django-backup/django-backup)), along with a proper mirror (called a [hot standby](https://cloud.google.com/community/tutorials/setting-up-postgres-hot-standby)) of the database itself. An institution might simply want to mirror the filesystem, or to create freezes at consistent timepoints. The [InterPlanetary File System](https://en.wikipedia.org/wiki/InterPlanetary_File_System) has also been suggested, and we hope to have discussion and testing with the larger community to either provide a default or suggest top choices.

### How is a Singularity Registry different from a Docker Registry?

Both are similar, and in fact might be friends! We can easily talk about things they have in common:

 - both serve image manifests that link to relevant image files
 - both can be deployed for a single user or institution
 - both are Dockerized themselves

And things that are different:

 - A Docker registry serves layers (`.tar.gz`) and not entire images. A Singularity Registry serves entire images.
 - Any Docker image from a Docker Registry can be immediately converted to Singularity. As far as I know, the other way around is not developed.
 - Singularity Registry images can be pulled to a cluster resource. Docker images cannot.

There are really great use cases for both, and the decision of which to use is up to the goals of the user.

### Are there features of Singularity that are particularly supported by Singularity Hub?

Singularity aims to support scientific containers, so Singularity Hub and Registry take an extra step to serve metadata about the containers via the API. It's important to know about usage (downloads and stars) but also software, environment variables, labels, and runscripts. This supports being able to do more research analytics across containers to better understand how containers (and more broadly software) help answer scientific questions. Given the issues we have with reproducibility, this is essential.
