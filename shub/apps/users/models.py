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
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from shub.apps.users.utils import get_usertoken
from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime
import re

# 2) once a user is added, he/she should be able to use refresh token
# (eg add this http://getblimp.github.io/django-rest-framework-jwt/


class User(AbstractUser):
    active = models.BooleanField(default=True)         # allowed to build, etc.
    agree_terms = models.BooleanField(default=False)   # has the user agreed to terms?
    agree_terms_date = models.DateTimeField(blank=True,default=None,null=True)          # has the user agreed to terms?
    
    class Meta:
        app_label = 'users'
    
    def get_label(self):
        return "users"

    def token(self):
        return get_usertoken(self)


# Create a token for the user when the user is created (with oAuth2)
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
