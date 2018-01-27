---
layout: default
title: Credentials
pdf: true
permalink: /credentials
toc: false
---

After you create a user, you will need a way to communicate to the registry, and validate your identity. If we jump ahead and tried running the `sregistry` [client](/sregistry/client) we would see a message like this:

```
 sregistry list
ERROR Client secrets file not found at `/home/vanessa/.sregistry` or $SREGISTRY_CLIENT_SECRETS.
```

Ruhroh! The reason is because we need to put our credentials in a hidden file called `.sregistry` in our `$HOME` directory. Each time we use the client, the secrets is used to encrypt a call and time-specific token that the registry can un-encrypt with the same key, and verify the payload. After creating your account in [setup](/sregistry/setup), making yourself a superuser and admin and logging in (remember this part?)


```
NAME=$(docker ps -aqf "name=sregistry_uwsgi_1")
docker exec $NAME python /code/manage.py add_superuser --username vsoch
docker exec $NAME python /code/manage.py add_admin --username vsoch
```

You will want to go to [http://127.0.0.1/token](http://127.0.0.1/token) and copy paste the entire json object into a file called `.sregistry` in your `$HOME` folder. **Important** you must be a superuser **and** admin to build images. If you don't add yourself as an admin, the menu looks like this:

![/assets/img/without-superuser.png](/assets/img/without-superuser.png)

As an admin, you see the button for "token":

![/assets/img/with-superuser.png](/assets/img/with-superuser.png)


Here is the token page - note the button on the left will copy the text to your clipboard, for pasting in a file at `$HOME/sregistry`.

![/assets/img/token.png](/assets/img/token.png)

Now when we try to communicate with the client, it finds the token and can identify us. 

```
sregistry list
No container collections found.
```

Don't worry, I haven't showed you that command and toolset yet. The functions for doing this will be provided in [singularity-python](https://www.github.com/singularityware/singularity-python), but actually we will build a singularity image [in the next client instructions](/sregistry/client) to do this.

Next, see if you are interested in activating any additional [plugins](/sregistry/plugins) for your Singularity Registry.

<div>
    <a href="/sregistry/setup"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry/plugins"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
