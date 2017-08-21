# Setup
By the time you get here, you have added all required secrets and settings to your [settings](../shub/settings) folder, and you've built and started the image. Next, you should navigate to [http://127.0.0.1](http://127.0.0.1) (localhost) to make sure the registry is up and running. 

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

## Accounts
To create your admin account, the first thing you need to do (in the web interface) is click Login on the top right. You should see the social account options that you configured in the [deployment](deployment.md) step. You can now log in with your social account of choice. This will create a user account for yourself that you can use to manage the application, and when you are logged in you should see your username in the top right. It usually corresponds with the one from your social account.


## The Application Manager
At this point, you've started the application, and created a user with your social auth. Your username is in the top right, and it's usually the same as your social account. Keep this in mind because you will need it when you shell into the image to make yourself a superuser. Let's first shell inside:

```
NAME=$(docker ps -aqf "name=sregistry_uwsgi_1")
docker exec -it ${NAME} bash
```

you will find yourself in a directory called `/code`, which is where the main application lives. For administration you will be using the file [manage.py](../manage.py) to interact with the registry. If you want to see all the different options, type `python manage.py` and it will show you.

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
```

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

Great! Now that you have your accounts, you probably want to learn about how to build and push images! You will need to read about the [client](client.md) to do this.
