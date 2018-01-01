'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017 Vanessa Sochat.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.fields import JSONField
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
    admin = models.BooleanField(default=False)         # is this a registry admin?
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
