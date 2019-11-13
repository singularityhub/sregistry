---
title: Robot Users
pdf: true
toc: false
---

# How to Generate a Robot User

In the case that you want to generate a robot user, or an account not associated with
a real person that can push from some CI service, you'll need to do the following.

{% include alert.html type="info" title="Important!" content="You must be an admin of the server to generate a robot user." %}

 1. Use the Django Administration site to add this user and a token for this user will be automatically created. If you need to refresh the token, you can do so here.
 2. Since the collection must already exist and you cannot log in as the robot user, you should create the collection with your user account, and then you can add the robot user as an owner (shown below). Only owners are allowed to push to collections. 

First, enter the uwsgi container (the name of your container may be different)

```bash
docker exec -it sregistry_uwsgi_1 bash
python manage.py shell
```

Find your robot user, and your collection:

```python
from shub.apps.users.models import User
from shub.apps.main.models import Collection
user = User.objects.get(username="myuser")
collection = Collection.objects.get(name="mycollection")
```

And then add the robot user as an owner to it.

```python
collection.owners.add(user)
collection.save()
```

As an alternative, if you intend to add this robot user to more than one collection,
you can create a [Team]({{ site.url }}{{ site.baseurl }}/docs/setup/teams) in the interface, 
add the robot user to it also via the console:

```python
from shub.apps.users.models import Team, User
team = Team.objects.get(name="myteam")
user = User.objects.get(username="myuser")
team.members.add(user)
```

And then in any collection interface where you can see the team, you can add
the robot user directly as an owner.

And that's it!
