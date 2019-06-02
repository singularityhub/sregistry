'''

Copyright (C) 2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import FileSystemStorage
from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
import uuid
import time
import hashlib
import os


class RecipeFile(models.Model):
    '''a RecipeFile is a Singularity Recipe pushed to do a remote build.
    '''
    created = models.DateTimeField(auto_now_add=True)
    collection = models.CharField(max_length=200, null=False)
    tag = models.CharField(max_length=200, null=False)
    name = models.CharField(max_length=200, null=False)
    owner_id = models.CharField(max_length=200, null=True)
    datafile = models.FileField(upload_to=get_upload_folder,
                                max_length=255,
                                storage=OverwriteStorage())

    def get_label(self):
        return "recipefile"

    def get_abspath(self):
        return os.path.join(settings.MEDIA_ROOT, self.datafile.name)

    class Meta:
        app_label = 'api'


# Trigger a build when a recipe is uploaded
post_save.connect(trigger_build, sender=RecipeFile)
