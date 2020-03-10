---
title: collection interface
pdf: true
toc: false
---

# Interfaces

## Teams

Singularity Registry Server allows registry staff (and if the administrators allow it) authenticated users to create teams, or groups of users that want to collaborate on container collections together.

![teams.png](../assets/img/teams.png)

If you are allowed to create and manage teams (see the setup page section about [teams](/sregistry/setup#teams) for information about this) the team permission level determines how others are added to the team.  If a team is **open**, then anyone can join. If it's **invite** only, then you need to generate an invitation. To do this, you can navigate to your Team page, and click the button to "Invite User":

![team-invite.png](../assets/img/team-invite.png)

The interface will give you a link to send to your colleague to join him or her to the team. Once used, it will expire.

![team-invite-link.png](../assets/img/team-invite-link.png)

Membership in teams is important because when you add another user as a collaborator to one of your collections (either an owner ot member) they must be part of one of your teams.

### Admin Control of Teams

While Singularity Registry server doesn't directly allow administrators to add any users to be part of a
collection contributors or owners (this we believe should be up to the collection owners), it is possible to do this
programmatically if it's absolutely necessary. Here is an example:

```python
# $ docker exec -it sregistry_uwsgi_1 bash
# python manage.py shell
from shub.apps.main.models import Collection
from shub.apps.users.models import User

# Target a collection and user
collection = Collection.objects.get(name="collection")
user = User.objects.get(username='vsoch')

# Who are current contributors, owners?
collection.contributors.all()                                                                                                          
collection.owners.all()      

# Add to contributors and/or owners
collection.contributors.add(user)
collection.owners.add(user)
```

It is the philosophy of this developer that collection owners should be responsible for this,
and thus the "Teams" feature is advocated for use as it explicitly states "I am creating
this team of trusted users to add to my collection."


## Collections 
A collection is a set of containers under the same namespace. For example, `dinosaur/avocado` and `dinosaur/banana` could be two containers in the `dinosaur` collection. You can browse all collections
in the main collection view:

![collections.png](../assets/img/collections.png)

and browse the containers within a collection by clicking on it:

![collection.png](../assets/img/collection.png)

### Add a Container
A view has been added for users with permission to directly upload a container to a collection! You
can do this by clicking the "+" in the menu above the container table. here is what the upload page looks like:

![upload.png](../assets/img/upload.png)

This uploads directly to nginx via the [nginx upload module](https://www.nginx.com/resources/wiki/modules/upload/), so it should be pretty speedy.


## Collection Settings

The most important control panel for your collections is the Settings page, which we
see as the first link in the menu at the top of the table. The most likely action you will want to do is add other users from your teams (as described above). You do this on each Collection settings page:

![team-settings.png](../assets/img/team-settings.png)

For example, if my lab has a set of users on sregistry and we intend to build images together, we would make a team for our lab, and then easily find one another to manage access to images.

### Badges
Recently added, you can get a badge to link to your collection

![assets/img/badges.png](../assets/img/badges.png)

### Users
You might want to give other users control of your collection (to push and pull and generally manage), and these are called **owners**. You might also want to give some users pull access, most relevant if your collection is private. You can do that in the "Contributors" tab of the settings page:

![assets/img/team-settings.png](../assets/img/team-settings.png)

Remember that you can only choose to add individuals that are part of one of your teams. This means that you should generally make a team first.

### Danger Zone
And of course if you need to delete, the settings page has a Danger Zone. Be careful!

![assets/img/danger.png](../assets/img/danger.png)
