'''

Copyright (c) 2017, Vanessa Sochat, All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''


from django.core.files.storage import FileSystemStorage
from django.contrib.postgres.fields import JSONField
from shub.settings import MEDIA_ROOT
from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
import os
import json

class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name, max_length=None):
        # If the filename already exists, remove it as if it was a true file system
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


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
        collection.save()

    # Create collection root, if it doesn't exist
    image_home = "%s/%s" %(MEDIA_ROOT,collection_name)
    if not os.path.exists(image_home):
        os.mkdir(image_home)
    
    # Create a container, or get it, if doesn't exist
    return os.path.join(image_home, filename)


class ImageFile(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    collection = models.CharField(max_length=200, null=False)
    tag = models.CharField(max_length=200, null=False)
    metadata = models.TextField(default='') # will be converted to json
    name = models.CharField(max_length=200, null=False)
    datafile = models.FileField(upload_to=get_upload_folder,storage=OverwriteStorage())

                   # ImageFile (instance)
def create_container(sender, instance, **kwargs):
    from shub.apps.main.models import Container, Collection
    from shub.apps.main.views import update_container_labels
    collection = Collection.objects.get(name=instance.collection)
    metadata = instance.metadata
   
    # Get a container, if it exists, we've already written file here
    containers = collection.containers.filter(tag=instance.tag)
    if len(containers) > 0:
        container = containers[0]
    else:
        container = Container.objects.create(collection=collection,
                                             tag=instance.tag,
                                             name=instance.name,
                                             image=instance)
        
    def add_metadata(container,metadata,field):
        if field in metadata:
            if field not in ['',None]:
                container.metadata[field] = metadata[field]
                container.save()

    # Load container metadata
    #try:
    metadata = json.loads(metadata)['data']['attributes']
    add_metadata(container,metadata,'deffile')
    add_metadata(container,metadata,'runscript')
    add_metadata(container,metadata,'test')
    add_metadata(container,metadata,'environment')

    #except:
    #    bot.error("Error parsing metadata for %s/%s" %(collection.name,
    #                                                   instance.name))
    #    pass

    # Add labels
    if metadata['labels'] not in [None,'']:
        container = update_container_labels(container,metadata['labels'])

    container.save()

post_save.connect(create_container, sender=ImageFile)
