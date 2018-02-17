---
layout: default
title: Setup
pdf: true
permalink: /setup
toc: false
---

# Setup
By the time you get here, you have added all required secrets and settings to your [settings](https://github.com/singularityhub/sregistry/tree/master/shub/settings) folder, and you've built and started the image. Next, you should navigate to [http://127.0.0.1](http://127.0.0.1) (localhost) to make sure the registry is up and running. 

## Image Interaction
Before we work with accounts and other application setup, you need to know how to interact with the application, meaning Docker images. Here are the basic commands you should get comfortable with as an administrator of your registry. Note that these are really great for debugging too:

```
docker ps  # gets you the image ids
docker-compose logs worker  # show me the logs of the worker instance
docker-compose logs nginx  # logs for the main application
docker-compose logs -f nginx  # keep the logs open until I Control+C
```

and to shell in to an image, you can do the following:

```
NAME=$(docker ps -aqf "name=sregistry_uwsgi_1")
docker exec -it ${NAME} bash
```

## Roles
Before we make accounts, let's talk about the different roles that can be associated with a registry. The core of Django supports some pre-defined roles, and we use those to the greatest extent that we can to keep things simple.

admin (a collection admin) is just a user that can create his/her own collections (via a push) given that the registry admin has enabled USER_COLLECTIONS
And then for each collection, the default is that it's public for pull. If the user makes it private, he/she can add/remove people to give permission to pull. They will be stored in a "collaborators" field of the collection.

I'm thinking about the idea of adding a "Team" (or organization, or group, or lab) but not decided.


### superuser
You can think of as an application master. They have the highest level of permissions (akin to root) to shell into the application, add and remove users and roles, and do pretty much whatever they want. In that you are reading this and setting up the registry, you are going to be a superuser.

### admin
An admin corresponds with Django's "staff" role. An admin is designated by the superuser to have global ability to manage collections. This means the admin has a credential file to push images. An admin is a manager, but only of container collections, not the application.

### authenticated user
is a user that creates an account via the interface, but does not have a global ability to push images. Instead, the authenticated user can edit and manage collections that he or she contributes to.
  - If the variable `USER_COLLECTIONS` is set to True, the authenticated user can create and manage collections. Each collection can have one or more owners and contributors, and both can push and pull images. Only owners can delete the collection or containers within it.
  - If the variable `USER_COLLECTIONS` is False, the authenticated user cannot create his or her own collections, but can still be added as a contributor to collections managed by admins.

Since you get to choose your authentication backend (e.g., LDAP, Twitter) you get to decide who can become an authenticated user. Here are a couple of scenarios:

 - You can keep container management tightly controlled by setting `USER_COLLECTIONS` to False, and then making a small set of individuals `admin`, meaning they manage public and/or private collections of containers for all users. In the case that a collection is private, the authenticated users must be added as contributors in the settings to view and pull images.
 - You can allow your users to manage their own collections and images by setting `USER_COLLECTIONS` to True. You can still have `admin` roles to be global managers, but put users in charge of managing their own images. The same rules apply with public and private collections - if a collection is private, the user would need to add collaborators to give pull ability.

### visitors
is an anonymous user of the registry. In the case of a private registry, this individual cannot pull images. In the case of a public registry, there is no huge benefit to being authenticated.

Based on the above and granted that you are setting up the server and reading this, you will be a **superuser** because you have permissions to control the Docker images and grant other users (and yourself) the ability to push with the role **admin**.

## Teams
To add a level of organization of users, sregistry has created loose groups of users called Teams. Any authenticated user can create a team, meaning he or she becomes the Owner of the team that can add and remove users. There are two kinds of teams:

 - **invite** only means that an owner must send an invitation link.
 - **open** means that anyone can join the team that is authenticated in the registry.

The default setting is "invite." Teams are important because when you add individuals as collaborators to your collections, they must come from one of your teams. For example, if my lab has a set of users on sregistry and we intend to build images together, we would make a team for our lab, and then easily find one another to manage access to images.


## Create Accounts
To create your admin account, the first thing you need to do (in the web interface) is click Login on the top right. You should see the social account options that you configured in the [install](/sregistry/install) step. You can now log in with your social account of choice. This will create a user account for yourself that you can use to manage the application, and when you are logged in you should see your username in the top right. It usually corresponds with the one from your social account.


## The Application Manager
At this point, you've started the application, and created a user with your social auth. Your username is in the top right, and it's usually the same as your social account. Keep this in mind because you will need it when you shell into the image to make yourself a superuser. Let's first shell inside:

```
NAME=$(docker ps -aqf "name=sregistry_uwsgi_1")
docker exec -it ${NAME} bash
```

you will find yourself in a directory called `/code`, which is where the main application lives. For administration you will be using the file [manage.py](https://github.com/singularityhub/sregistry/blob/master/manage.py) to interact with the registry. If you want to see all the different options, type `python manage.py` and it will show you.

Let's first make yourself a superuser and an admin, meaning that you are an administrator **and** have godlevel control of the registry. Just by way of being inside the Docker image you already have that. You will be able to set other people as admins. In summary:

 - `superuser`: you are an admin that can do anything, you have all permissions.
 - `admin`: you can push images, but not have significant impact on the registry application.

Of course anyone that shells into your Docker image could just explode everything - it's up to you to secure and manage the server itself! Let's say my username is `vsoch`. Here is the command I would run to make myself a superuser and admin. Note that we are inside the Docker image `sregistry_uwsgi_1`:

```bash
$ python manage.py add_superuser --username vsoch
DEBUG Username: vsoch
DEBUG vsoch is now a superuser.

$ python manage.py add_superuser --username vsoch
DEBUG Username: vsoch
DEBUG vsoch can now manage and build.

# And from outside the Docker image
NAME=$(docker ps -aqf "name=sregistry_uwsgi_1")
docker exec $NAME python /code/manage.py add_superuser --username vsoch
docker exec $NAME python /code/manage.py add_admin --username vsoch

```

You can also choose to remove a superuser or admin at any time. This means he or she will no longer be able to build and access the token and secret to do so.


```
# Inside the image
$ python manage.py remove_superuser --username vsoch
$ python manage.py remove_admin --username vsoch

# Outside
NAME=$(docker ps -aqf "name=sregistry_uwsgi_1")
docker exec $NAME python /code/manage.py remove_superuser --username vsoch
docker exec $NAME python /code/manage.py remove_admin --username vsoch
```

## Registration
We maintain a "registry of registries" ([https://singularityhub.github.io/containers](https://singularityhub.github.io/containers))(one registry to rule them all...) where you can easily have your registry's public images available for others to find. Adding your registry is easy - it comes down to automatically generating a file, adding it to the repo, and then doing a pull request (PR). Specifically:


### 1. Fork the repo
Fork the repo, and clone to your machine. That might look like this, given a username `vsoch`:

```
git clone https://www.github.com/vsoch/containers
cd containers
```

### 2. Generate your Metadata
Then use the manager to generate a markdown file for your registry:

```
# Inside the image
$ python manage.py register

Registry template written to taco-registry.md!

Your robot is at https://vsoch.github.io/robots/assets/img/robots/robot5413.png
1. Fork and clone https://www.github.com/singularityhub/sregistry
2. Add taco-registry.md to the registries folder
3. Download your robot (or add custom institution image) under assets/img/[custom/robots]
4. Submit a PR to validate your registry.
```

Specifically, this produces a markdown file in the present working directory (which is mapped to your host) that can be plopped into a folder. It is named based on your registry `uri`, and looks like this:

```
$ cat taco-registry.md 
---
layout: registry
title:  "Tacosaurus Computing Center"
base: http://127.0.0.1
date:   2017-08-30 17:45:44
author: vsochat
categories:
- registry
img: robots/robot5413.png
thumb: robots/robot5413.png # wget https://vsoch.github.io/robots/assets/img/robots/robot15570.png
tagged: taco
institution: Tacosaurus Computing Center
---

Tacosaurus Computing Center is a Singularity Registry to provide institution level Singularity containers.

```

### 3. Choose your image
For the image and thumbnail, we have a [database of robots](https://vsoch.github.io/robots) that we have randomly selected a robot for you. If you don't like your robot, feel free to browse and choose a different one. Importantly, you will need to add the robot to the github repo:

```
cd containers/assets/img/robots
wget https://vsoch.github.io/robots/assets/img/robots/robot15570.png
```

If you have some other custom image, add it to the "custom" folder. If it's not created yet, make it.

```
cd containers/assets/img
mkdir -p custom
cd custom
mv /path/to/institution/logo/taco-logo.png
```

Then for each of the `thumb` and `img` fields you would want to look like this:

```
img: custom/taco-logo.png
thumb: custom/taco-logo.png
```

### 4. Submit a PR
You can then add your files, and submit a PR to the main repo. We will have tests that ping your registry to ensure correct naming of files and registry address, along with a preview of the content that is added. If you want to prevew locally, you can run `jekyll serve`.


Great! Now that you have your accounts, you probably want to learn about how to build and push images! First you need to generate a [credential](/sregistry/credentials), and then you will can read about the [client](/sregistry/client).

<div>
    <a href="/sregistry/install"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry/credentials"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
