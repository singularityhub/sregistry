'''

Copyright (C) 2017-2018 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017-2018 Vanessa Sochat.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

'''

from django.conf import settings
from django.contrib.auth.models import Group
from django.db.models.signals import ( post_save, pre_save )
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from shub.apps.users.utils import get_usertoken
from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime
import re


################################################################################
# Supporting Functions
################################################################################


# Get path to where images are stored for teams
def get_image_path(instance, filename):
    team_folder = os.path.join(settings.MEDIA_ROOT, 'teams')
    if not os.path.exists(team_folder):
        os.mkdir(team_folder)
    return os.path.join('teams', filename)


# 2) once a user is added, he/she should be able to use refresh token
# (eg add this http://getblimp.github.io/django-rest-framework-jwt/


class User(AbstractUser):
    active = models.BooleanField(default=True)

    # has the user agreed to terms?
    agree_terms = models.BooleanField(default=False)
    agree_terms_date = models.DateTimeField(blank=True,
                                            default=None,
                                            null=True)     

    
    class Meta:
        app_label = 'users'
    
    def get_label(self):
        return "users"

    def token(self):
        return get_usertoken(self)



################################################################################
# Teams
################################################################################

class Team(models.Model):
    '''A team is a group of users with shared affiliation. One or more owners
       can edit the team name, photo, etc. Each user can join one or more
       teams.
    '''

    name = models.CharField(max_length=50,
                            null=False,
                            blank=False,
                            unique=True)

    # Each team has a group created with the same name.
    group = models.OneToOneField(Group, 
                                 on_delete=models.CASCADE, 
                                 primary_key=True)

    owners = models.ManyToManyField(User, blank=True,
                                    related_name="team_owners",
                                    related_query_name="team_owners", 
                                    help_text="Administrators of the team.")

    created_at = models.DateTimeField('date of creation', auto_now_add=True)
    updated_at = models.DateTimeField('date of last update', auto_now=True)

    team_image = models.ImageField(upload_to=get_image_path,
                                   blank=True, null=True) 

        
    def __str__(self):
        return "%s:%s" %(self.id,self.name)

    def __unicode__(self):
        return "%s:%s" %(self.id,self.name)

    def get_label(self):
        return "users"

    class Meta:
        app_label = 'users'



################################################################################
# Post Save
################################################################################


@receiver(pre_save, sender=Team)
def create_team_group(sender, instance, created, **kwargs):

    # Get the name from the team
    name = (name.replace(' ','-').lower().strip()
                                 .decode('utf-8','ignore')
                                 .encode("utf-8"))
    instance.name = name
    new_group, _ = Group.objects.get_or_create(name=name)
    
    # Does the group get assigned some permission here? 


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    ''' Create a token for the user when the user is created (with oAuth2)

        1. Assign user a token
        2. Assign user to default group

        Create a Profile instance for all newly created User instances. We only
        run on user creation to avoid having to check for existence on each call
        to User.save.

    '''
    if created:
        Token.objects.create(user=instance)

    ''' Assign groups
    if created and instance.username != settings.ANONYMOUS_USER_NAME:
        from profiles.models import Profile
        profile = Profile.objects.create(pk=user.pk, user=user, creator=user)

        # Create collections?
        assign_perm("change_user", user, user)
        assign_perm("change_profile", user, profile)'''
