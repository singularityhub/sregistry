"""

Copyright 2017-2023 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

import os
from itertools import chain

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse
from rest_framework.authtoken.models import Token

from shub.apps.users.utils import get_usertoken

################################################################################
# Supporting Functions
################################################################################


# Get path to where images are stored for teams
def get_image_path(instance, filename):
    team_folder = os.path.join(settings.MEDIA_ROOT, "teams")
    if not os.path.exists(team_folder):
        os.mkdir(team_folder)
    return os.path.join("teams", filename)


TEAM_TYPES = (
    ("invite", "Invite only. The user must be invited by an owner"),
    ("open", "Open. Anyone can join the team without asking."),
)


class CustomUserManager(BaseUserManager):
    def _create_user(
        self, username, email, password, is_staff, is_superuser, **extra_fields
    ):
        """
        Creates and saves a User with the given username, email and password.
        """
        if not username:
            raise ValueError("The given username must be set")

        email = self.normalize_email(email)
        user = self.model(
            username=username.lower(),
            email=email,
            is_staff=is_staff,
            is_active=True,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        return self._create_user(
            username, email, password, False, False, **extra_fields
        )

    def create_superuser(self, username, email, password, **extra_fields):
        return self._create_user(username, email, password, True, True, **extra_fields)

    def add_superuser(self, user):
        """Intended for existing user"""
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def add_staff(self, user):
        """Intended for existing user"""
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    active = models.BooleanField(default=True)

    # has the user agreed to terms?
    agree_terms = models.BooleanField(default=False)
    agree_terms_date = models.DateTimeField(blank=True, default=None, null=True)

    # Ensure that we can add staff / superuser and retain on logout
    objects = CustomUserManager()

    class Meta:
        app_label = "users"

    def has_create_permission(self):
        """has create permission determines if the user (globally) can create
        new collections. By default, superusers and admin can, along with
        regular users if USER_COLLECTIONS is True. Otherwise, not.
        """
        if self.is_superuser is True or self.is_staff is True:
            return True
        if settings.USER_COLLECTIONS is True:
            return True
        return False

    def is_team_member(self, collection):
        """given a collection, determine if the user is member of any teams
        associated with the collection
        """
        for owner in collection.owners.all():
            for team in owner.team_owners.all():
                if self in team.members.all():
                    return True
        return False

    def is_team_owner(self, collection):
        """given a collection, determine if the user is owner of any teams
        associated with the collection
        """
        for owner in collection.owners.all():
            for team in owner.team_owners.all():
                if self in team.owners.all():
                    return True
        return False

    def get_credentials(self, provider):
        """return one or more credentials, or None"""
        if self.is_anonymous is False:
            try:
                # Case 1: one credential
                credential = self.social_auth.get(provider=provider)
                return credential
            except Exception:
                # Case 2: more than one credential for the provider
                credential = self.social_auth.filter(provider=provider)
                if credential:
                    return credential.last()

    def get_providers(self):
        """return a list of providers that the user has credentials for."""
        return [x.provider for x in self.social_auth.all()]

    def get_label(self):
        return "users"

    @property
    def token(self):
        return get_usertoken(self)


################################################################################
# Teams
################################################################################


class Team(models.Model):
    """A team is a group of users with shared affiliation. One or more owners
    can edit the team name, photo, etc. Each user can join one or more
    teams.
    """

    name = models.CharField(max_length=50, unique=True, default=None)

    owners = models.ManyToManyField(
        User,
        blank=True,
        default=None,
        related_name="team_owners",
        related_query_name="team_owners",
        help_text="Administrators of the team.",
    )

    members = models.ManyToManyField(
        User,
        blank=True,
        default=None,
        related_name="contributors",
        related_query_name="contributors",
        help_text="Contributors to the team.",
    )

    created_at = models.DateTimeField("date of creation", auto_now_add=True)
    updated_at = models.DateTimeField("date of last update", auto_now=True)

    permission = models.CharField(
        choices=TEAM_TYPES,
        default="invite",
        max_length=100,
        verbose_name="Permission needed to join team",
    )

    team_image = models.ImageField(upload_to=get_image_path, blank=True, null=True)

    def get_members(self):
        """get a list of unique members, including both contributors and owners"""
        members = chain(self.owners.all(), self.members.all())
        return list(set(list(members)))

    def get_invite(self, code):
        """get the invitation for a user, if it exists.

        Parameters
        ==========
        code: the code to validate the invitation
        """
        keyargs = {"code": code, "team": self}
        try:
            invite = MembershipInvite.objects.get(**keyargs)
        except MembershipInvite.DoesNotExist:
            return None
        else:
            return invite

    def add_member(self, user, code=None):
        """add a user to a team. If a code is provided,
        the invitation object is deleted.

        Parameters
        ==========
        user: the user to add as a member
        code: if provided, ensure valid, then delete

        """
        if code is not None:
            invitation = self.get_invite(code)
            if invitation is not None:
                invitation.delete()

        # Finally, add the user
        self.members.add(user)
        self.save()
        return self

    def has_edit_permission(self, request):
        """determine if a user has edit permission for a team.

        1. A superuser has edit permission, always
        2. A global admin has edit permission, always
        3. A user has edit permission if is one of the owners

        """
        # Global edit permission for superuser and staff
        if request.user.is_superuser or request.user.is_staff:
            return True

        # Edit permission to owners given so
        elif request.user in self.owners.all():
            return True

        return False

    def get_absolute_url(self):
        return reverse("team_details", args=[str(self.id)])

    def has_member(self, username):
        """return True if the username is either a member or owner for the team

        Parameters
        ==========
        username: the username to check
        """
        members = self.get_members()
        names = [x.username for x in members]
        if username in names:
            return True
        return False

    def __str__(self):
        return "%s" % self.name

    def __unicode__(self):
        return "%s" % self.name

    def get_label(self):
        return "users"

    class Meta:
        app_label = "users"


class MembershipInvite(models.Model):
    """An invitation to join a team."""

    code = models.CharField(max_length=200, null=False, blank=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return "<%s:%s>" % (self.id, self.team.name)

    def __unicode__(self):
        return "<%s:%s>" % (self.id, self.team.name)

    def get_label(self):
        return "users"

    def get_url(self):
        """return the reverse, invitation link for the user to follow"""
        return "%s%s" % (
            settings.DOMAIN_NAME,
            reverse("join_team", args=[self.team.id, self.code]),
        )

    class Meta:
        app_label = "users"
        unique_together = (("code", "team"),)


################################################################################
# Post Save
################################################################################


@receiver(pre_save, sender=Team)
def create_team_group(sender, instance, **kwargs):
    # Get the name from the team
    name = instance.name.replace(" ", "-").lower().strip()
    instance.name = name


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """Create a token for the user when the user is created (with oAuth2)

    1. Assign user a token
    2. Assign user to default group

    Create a Profile instance for all newly created User instances. We only
    run on user creation to avoid having to check for existence on each call
    to User.save.

    """
    if created:
        Token.objects.create(user=instance)
