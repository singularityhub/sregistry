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

from shub.settings import MEDIA_ROOT
from sregistry.utils import parse_image_name
from shub.logger import bot
import shutil
import json
import os

def move_upload_to_storage(collection, upload_id):
    '''moving an uploaded *ChunkedImage* to storage means:
         1. create a folder for the collection, if doesn't exist
         2. an image in storage. It will be moved here from
       the temporary upload and renamed
    '''
    from shub.apps.api.models import ChunkedImage

    # Get ImageFile instance, rename the file
    instance = ChunkedImage.objects.get(upload_id=upload_id)

    # Create collection root, if it doesn't exist
    image_home = "%s/%s" %(MEDIA_ROOT, collection.name)
    if not os.path.exists(image_home):
        os.mkdir(image_home)
    
    # Rename the file, moving from ChunkedUpload to Storage
    filename = os.path.basename(instance.file.path)
    new_path = os.path.join(image_home, filename.replace('.part', '.simg'))
    shutil.move(instance.file.path, new_path)
    print('%s --> %s' %(instance.file.path, new_path))
    instance.file.name = new_path
    instance.save()

    return instance


def upload_container(cid, request, upload_id, name, version):
    '''upload container is the function called by the ChunkedUpload
       after a chunked upload save (from the web interface or push)
       Note that this is ineffecient, we probably should not have the trigger
       happen so frequently but this will work for now :)

       Parameters
       ==========
       cid: the collection id to add the container to
       user: the user that has requested the upload
       upload_id: the upload_id to find the container
       name: the requested name for the container
       version: the md5 sum of the file

    '''
    from shub.apps.main.models import ( Container, Collection )
    from shub.apps.api.models import ( ChunkedImage, ImageFile )
    from shub.apps.main.views import update_container_labels
    collection = Collection.objects.get(id=cid)

    # Only continue if edit permission is okay
    if collection.has_edit_permission(request):

        # parse the image name, get the datafile
        names = parse_image_name(name, version=version)
        instance = move_upload_to_storage(collection, upload_id)

        image = ImageFile.objects.create(collection=collection,
                                         tag=names['tag'],
                                         name=names['uri'],
                                         owner_id=request.user.id,
                                         datafile=instance.file)

        # Get a container, if it exists (and the user is re-using a name)
        containers = collection.containers.filter(tag=names['tag'],
                                                  name=names['uri'])

        # If one exists, we check if it's frozen
        create_new = True
        if len(containers) > 0:

            # If we already have a container, it might be frozen
            container = containers[0]

            # If it's frozen, create a new one
            if container.frozen is False:
                create_new = False

         
        if create_new is True:
            container = Container.objects.create(collection=collection,
                                                 name=names['image'],
                                                 tag=names['tag'],
                                                 image=image,
                                                 version=names['version'])

        # Otherwise, use the same container object, but update version
        else:
            container.version = names['version']
       
        container.save()

        # Once the container is saved, delete the intermediate file object
        instance.file = None
        instance.save()
        instance.delete()


def create_container(sender, instance, **kwargs):
    '''create container is the function called by the ImageFile (in models.py)
       after a push to the registry, triggered by ContainerPushSerializer.

       Parameters
       ==========
       sender: should be the sending model, which is an ImageFile instance
       instance: is the instance of the ImageFile

    '''
    from shub.apps.users.models import User
    from shub.apps.main.models import Container, Collection
    from shub.apps.main.views import update_container_labels

    collection = Collection.objects.get(name=instance.collection)
    metadata = instance.metadata

    # Add the owner
    try:
        owner = User.objects.get(id=instance.owner_id)
        collection.owners.add(owner)
        collection.save()
    except:
        pass   

    # Get a container, if it exists, we've already written file here
    containers = collection.containers.filter(tag=instance.tag,
                                              name=instance.name)
    if len(containers) > 0:
        container = containers[0]
    else:
        container = Container.objects.create(collection=collection,
                                             tag=instance.tag,
                                             name=instance.name,
                                             image=instance)
        
    def add_metadata(container,metadata,field):
        if field in metadata:
            if field not in ['', None]:
                container.metadata[field] = metadata[field]
                container.save()

    # Load container metadata
    metadata = json.loads(metadata)['data']['attributes']
    add_metadata(container, metadata, 'deffile')
    add_metadata(container, metadata, 'runscript')
    add_metadata(container, metadata, 'test')
    add_metadata(container, metadata, 'environment')

    # If exists, add size
    try:
        container_size = metadata['labels']['SREGISTRY_SIZE_MB']
        container.metadata['size_mb'] = container_size
        container.save()
    except:
        pass

    # If exists, add From line as tag
    try:
        container_from = metadata['labels']['SREGISTRY_FROM']
        container.tags.add(container_from)
        container.save()
    except:
        pass

    # Add labels
    if metadata['labels'] not in [None, '']:
        container = update_container_labels(container,metadata['labels'])

    container.save()
