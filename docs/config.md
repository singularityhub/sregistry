# Getting Started
By the time you get here, you have added all required secrets and settings to your [settings](../shub/settings) folder, and you've built and started the image. Next, you should navigate to [http://127.0.0.1](http://127.0.0.1) (localhost) to make sure the registry is up and running. If you need to look at logs or shell into the image to poke around, here are your debugging gotos:


```
docker ps  # gets you the image ids
docker-compose logs worker  # show me the logs of the worker instance
docker-compose logs nginx  # logs for the main application

```

and to shell in to an image, you can do the following:

```
NAME=$(docker ps -aqf "name=sregistry_uwsgi_1")
docker exec -it ${NAME} bash
```

When you see the interface, click Login on the top right and log in with your social account of choice. This will create a user account for yourself that you can use to manage the application.


## The Application Manager
At this point, you've started the application, and created a user with your social auth. Your username is in the top right, and it's usually the same as your social account. Keep this in mind because you will need it when you shell into the image to make yourself a superuser. Let's first shell inside:

```
NAME=$(docker ps -aqf "name=sregistry_uwsgi_1")
docker exec -it ${NAME} bash
```

you will find yourself in a directory called `/code`, which is where the main application lives. For administration you will be using the file [manage.py](../manage.py) to interact with the registry. If you want to see all the different options, type `python manage.py` and it will show you.

Let's first make yourself a superuser, meaning that you are an administrator **and** manager of the registry. You will be able to set other people as managers, who can push images but not be admins. In summary:

 - `superuser`: you are an admin that can do anything, and you can pull images like managers.
 - `manager`: you can push images, but not admin the registry

Of course anyone that shells into your Docker image could just explode everything - it's up to you to secure and manage the server itself! Let's say my username is `vsoch`. Here is the command I would run:

```bash
# Inside the image, here is how you would do it
$ python manage.py add_superuser --username vsoch
DEBUG Username: vsoch
DEBUG vsoch can now manage and build.

```
# And from outside the Docker image

NAME=$(docker ps -aqf "name=sregistry_uwsgi_1")
docker exec $NAME python /code/manage.py add_superuser --username vsoch
```

You can also choose to remove a superuser at any time. This means he or she will no longer be able to build and access the token and secret to do so.




## Adding users to a registry
A user that stumbles on your web interface can easily authenticate with a social account to look around. If you are OK with this, then we are good to go. However, in the case that you don't have a web UI, you can add users from the command line. Do this with caution, as it will be a username/password stored in the database, and not have a nice token / refresh token flow.

Let's say that we have a user with username `sputnick` and we want to add him to the registry. That would look like this:

```
python manage.py add_registry_user  --username sputnick --password sputnick 

DEBUG Username: sputnick
DEBUG Password: provided
DEBUG sputnick created successfully.
```

Great! Next you probably want to learn about how the [API]() works, which means granting tokens to admins to push built images, and connecting your registry to Singularity to make the images pull-able.
