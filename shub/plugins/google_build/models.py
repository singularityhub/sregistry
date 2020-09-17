"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
from shub.apps.api.models.storage import OverwriteStorage
from .actions import trigger_build
import uuid
import os


def get_upload_folder(instance, filename):
    """a helper function to upload a recipe file to storage."""
    from shub.apps.main.models import Collection

    collection_name = instance.collection.lower()
    instance.collection = collection_name

    # First get a collection
    try:
        collection = Collection.objects.get(name=collection_name)
    except Collection.DoesNotExist:
        collection = Collection.objects.create(name=collection_name)
        collection.secret = str(uuid.uuid4())
        collection.save()

    # Create collection root, if it doesn't exist
    image_home = os.path.join(settings.MEDIA_ROOT, collection_name)
    recipe_home = os.path.join(image_home, "recipes")

    for dirname in [image_home, recipe_home]:
        if not os.path.exists(dirname):
            os.mkdir(dirname)

    return os.path.join(recipe_home, filename)


class RecipeFile(models.Model):
    """a RecipeFile is a Singularity Recipe pushed to do a remote build."""

    created = models.DateTimeField(auto_now_add=True)
    collection = models.CharField(max_length=200, null=False)
    tag = models.CharField(max_length=200, null=False)
    name = models.CharField(max_length=200, null=False)
    owner_id = models.CharField(max_length=200, null=True)
    datafile = models.FileField(
        upload_to=get_upload_folder, max_length=255, storage=OverwriteStorage()
    )

    def get_label(self):
        return "recipefile"

    def __str__(self):
        if hasattr(self.datafile, "name"):
            return self.datafile.name
        return self.get_label()

    def get_abspath(self):
        return os.path.join(settings.MEDIA_ROOT, self.datafile.name)

    class Meta:
        app_label = "api"


# Trigger a build when a recipe is uploaded
post_save.connect(trigger_build, sender=RecipeFile)
