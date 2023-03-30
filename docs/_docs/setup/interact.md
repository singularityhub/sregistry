---
title: "Setup: Image Interaction"
pdf: true
toc: false
---

# Image Interaction

Before we work with accounts and other application setup, you need to know how to interact with the application, meaning Docker images. Here are the basic commands you should get comfortable with as an administrator of your registry. Note that these are really great for debugging too:

```
docker ps  # gets you the image ids
docker compose logs worker  # show me the logs of the worker instance
docker compose logs nginx  # logs for the main application
docker compose logs -f nginx  # keep the logs open until I Control+C
```

and to shell in to an image, you can do the following:

```
NAME=$(docker ps -aqf "name=sregistry_uwsgi_1")
docker exec -it ${NAME} bash
```

Next, learn how to [create and manage](roles) different user roles.
