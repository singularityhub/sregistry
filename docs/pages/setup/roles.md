---
layout: default
title: "Setup: User Roles"
pdf: true
permalink: /setup-roles
toc: false
---

# Roles
Before we make accounts, let's talk about the different roles that can be associated with a registry. The core of Django supports some pre-defined roles, and we use those to the greatest extent that we can to keep things simple.

## superuser
You can think of as an application master. They have the highest level of permissions (akin to root) to shell into the application, add and remove users and roles, and do pretty much whatever they want. In that you are reading this and setting up the registry, you are going to be a superuser.

## admin
An admin corresponds with Django's "staff" role. An admin is designated by the superuser to have global ability to manage collections. This also gives permission to create teams, or groups of one or more users that can be added as contributors to a collection. An admin has a credential file to push images. An admin is a manager, but only of container collections, not the application.

## authenticated user
is a user that creates an account via the interface, but does not have a global ability to push images. Instead, the authenticated user can edit and manage collections that he or she contributes to.
  - If the variable `USER_COLLECTIONS` is set to True, the authenticated user can create and manage collections, and create teams. Each collection can have one or more owners and contributors, and both can push and pull images. Only owners can delete the collection or containers within it.
  - If the variable `USER_COLLECTIONS` is False, the authenticated user cannot create his or her own collections, but can still be added as a contributor to collections managed by admins. In this case, the admin is also in charge of creating teams.

Since you get to choose your authentication backend (e.g., LDAP, Twitter) you get to decide who can become an authenticated user. Here are a couple of scenarios:

 - You can keep container management tightly controlled by setting `USER_COLLECTIONS` to False, and then making a small set of individuals `admin`, meaning they manage public and/or private collections and teams for all users. In the case that a collection is private, the authenticated users must be added as contributors in the settings to view and pull images.
 - You can allow your users to manage their own collections teams by setting `USER_COLLECTIONS` to True. You can still have `admin` roles to be global managers, but put users in charge of managing their own images. The same rules apply with public and private collections - if a collection is private, the user would need to add collaborators to give pull ability.

## visitors
is an anonymous user of the registry. In the case of a private registry, this individual cannot pull images. In the case of a public registry, there is no huge benefit to being authenticated.

Based on the above and granted that you are setting up the server and reading this, you will be a **superuser** because you have permissions to control the Docker images and grant other users (and yourself) the ability to push with the role **admin**.

# Google Build + GitHub

If you have enabled the [Google Build+Github]({{ site.baseurl }}/plugin-google-build) plugin,
then your users will be able to log in with GitHub, and build collections that are
linked to GitHub repositories. In this case, permissions for the registry interaction
do not extend to GitHub. For example, if you build from a repository that you own,
adding a collaborator or another owner will not change anything on GitHub.

Speaking of collaborators, next, learn how users can be a part of [teams](/sregistry/setup-teams)

<div>
    <a href="/sregistry/setup-interact"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry/setup-teams"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
