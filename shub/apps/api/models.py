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


from django.core.files.storage import FileSystemStorage
from shub.apps.api.actions import create_container
from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
import uuid
import os


#####################################################################################
# HELPERS
#####################################################################################


def get_upload_folder(instance,filename):
    '''a helper function to upload to storage
    '''
    from shub.apps.main.models import Container, Collection
    tag = instance.tag.lower()
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
    image_home = "%s/%s" %(settings.MEDIA_ROOT,collection_name)
    if not os.path.exists(image_home):
        os.mkdir(image_home)
    
    # Create a container, or get it, if doesn't exist
    return os.path.join(image_home, filename)



#####################################################################################
# MODELS & STORAGE
#####################################################################################


class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name, max_length=None):
        # If the filename already exists, remove it as if it was a true file system
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


class ImageFile(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    collection = models.CharField(max_length=200, null=False)
    tag = models.CharField(max_length=200, null=False)
    metadata = models.TextField(default='') # will be converted to json
    name = models.CharField(max_length=200, null=False)
    datafile = models.FileField(upload_to=get_upload_folder,storage=OverwriteStorage())

    def get_label(self):
        return "imagefile"

    class Meta:
        app_label = 'api'


post_save.connect(create_container, sender=ImageFile)
