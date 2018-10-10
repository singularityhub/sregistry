'''

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
from django.db import IntegrityError
from django.db.utils import DataError
import shutil
import uuid
import json
import os

def move_upload_to_storage(collection, upload_id):
    '''moving an uploaded *UploadImage* to storage means:
         1. create a folder for the collection, if doesn't exist
         2. an image in storage. It will be moved here from
       the temporary upload and renamed
    '''
    from shub.apps.api.models import ImageUpload

    # Get ImageFile instance, rename the file
    instance = ImageUpload.objects.get(upload_id=upload_id)

    # Create collection root, if it doesn't exist
    image_home = "%s/%s" %(MEDIA_ROOT, collection.name)
    if not os.path.exists(image_home):
        os.mkdir(image_home)
    
    # Rename the file, moving from ImageUpload to Storage
    filename = os.path.basename(instance.file.path)
    new_path = os.path.join(image_home, filename.replace('.part', '.simg'))
    shutil.move(instance.file.path, new_path)
    print('%s --> %s' %(instance.file.path, new_path))
    instance.file.name = new_path
    instance.save()
    return instance


def move_nginx_upload_to_storage(collection, source, dest):
    '''moving an uploaded file (from nginx module) to storage means.
         1. create a folder for the collection, if doesn't exist
         2. an image in storage pointing to the moved file

         Parameters
         ==========
         collection: the collection the image will belong to
         source: the source file (under /var/www/images/_upload/{0-9}
         dest: the destination filename
    '''
    # Create collection root, if it doesn't exist
    image_home = "%s/%s" %(MEDIA_ROOT, collection.name)
    if not os.path.exists(image_home):
        os.mkdir(image_home)
    
    new_path = os.path.join(image_home, os.path.basename(dest))
    shutil.move(source, new_path)
    return new_path


def upload_container(cid, user, name, version, upload_id, size=None):
    '''save an uploaded container, usually coming from an ImageUpload

       Parameters
       ==========
       cid: the collection id to add the container to
       user: the user that has requested the upload
       upload_id: the upload_id to find the container (for web UI upload)
                  if it exists as a file, an ImageUpload is created instead.
       name: the requested name for the container
       version: the md5 sum of the file

       Returns
       =======
       message: None on successful upload, specific error message. This is 
                a decision because it's purely intended to show to the user,
                if the function is used otherwise we would want these to be
                error / success codes.
    '''

    from shub.apps.main.models import ( Container, Collection )
    from shub.apps.api.models import ( ImageUpload, ImageFile )
    from shub.apps.main.views import update_container_labels
    collection = Collection.objects.get(id=cid)

    # Only continue if user is an owner
    if user in collection.owners.all():

        # parse the image name, get the datafile
        names = parse_image_name(name, version=version)

        # If the path exists, it's a file from nginx module, move to storage
        if os.path.exists(upload_id):
            storage = os.path.basename(names['storage'])
            new_path = move_nginx_upload_to_storage(collection, upload_id, storage)
            instance = ImageUpload.objects.create(file=new_path)
        else:
            instance = move_upload_to_storage(collection, upload_id)

        # Return an error to the user if the file is too big
        try:
            image = ImageFile.objects.create(collection=collection,
                                             tag=names['tag'],
                                             name=names['uri'],
                                             owner_id=user.id,
                                             datafile=instance.file)
        # Filename upper limit is 255
        except DataError as err:
            message = '%s\n%s must be less than 255 characters' %(err, 
                                                                  instance.file)
            bot.error(message)
            delete_file_instance(instance)
            return message

        # Get a container, if it exists (and the user is re-using a name)
        # Filter by negative id so we get the more recent container first.
        collection_set = collection.containers
        containers = collection_set.filter(tag=names['tag'],
                                           name=names['image']).order_by('-id')

        # If one exists, we check if it's frozen
        create_new = True

        if len(containers) > 0:

            # If we already have a container, it might be frozen
            container = containers[0]

            # If it's not frozen, overwrite the same file
            if container.frozen is False:
                container.delete()
                create_new = False
         
        # Container doesn't already exist / or old version isn't frozen
        if create_new is True:
            try:
                container = Container.objects.create(collection=collection,
                                                     name=names['image'],
                                                     tag=names['tag'],
                                                     image=image,
                                                     version=names['version'])

            # Catches when container is frozen, and version already exists
            except IntegrityError:
                message = '%s/%s:%s@%s already exists.' %(collection.name,
                                                          names['image'],
                                                          names['tag'],
                                                          names['version'])
                bot.error(message)
                delete_file_instance(instance)
                return message

        # Otherwise, use the same container object, but update version
        else:
            container.image = image
            container.version = names['version']
       
        container.save()

        # Save the size
        if size is None:
            size = os.path.getsize(instance.file.path) >> 20
        container.metadata['size_mb'] = size

        # Once the container is saved, delete the intermediate file object
        delete_file_instance(instance)


def delete_file_instance(instance):
    '''a helper function to remove the file assocation, and delete the instance
       if needed outside of this module can be added to models
    '''
    instance.file = None # remove the association
    instance.save()
    instance.delete()
