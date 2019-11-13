---
title: Robot Users
pdf: true
toc: false
---

## How to Generate a Robot User

In the case that you want to generate a robot user, or an account not associated with
a real person that can push from some CI service, you'll need to do the following.

{% include alert.html type="info" title="Important!" content="You must be an admin of the server to generate a robot user." %}

 1. Use the Django Administration site to add this user and a token for this user will be automatically created. If you need to refresh the token, you can do so here.
 2. Since the collection must already exist and you cannot log in as the robot user, you should create the collection with your user account, create a [team]({{ site.url }}{{ site.baseurl }}/docs/setup/teams) and add the collection to be owned by the team, and then add the robot user to the team inside the container like so:

First, enter the uwsgi container (the name of your container may be different)

```
docker exec -it sregistry_uwsgi_1 bash
python manage.py shell
```

Find your robot user, and your team (replace `gitlab-ci` with the name of your user)

```
from shub.apps.users.models import User, Team
user = User.objects.get(username="gitlab-ci")
team = Team.objects.get(name="myteam")
```

And then add the robot user as an owner to it.

```python
team.owners.add(user)
team.save()
```
