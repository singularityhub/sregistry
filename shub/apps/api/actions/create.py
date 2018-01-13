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

import json


                   # ImageFile (instance)
def create_container(sender, instance, **kwargs):
    from shub.apps.main.models import Container, Collection
    from shub.apps.main.views import update_container_labels

    collection = Collection.objects.get(name=instance.collection)
    metadata = instance.metadata
   
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
            if field not in ['',None]:
                container.metadata[field] = metadata[field]
                container.save()

    # Load container metadata
    metadata = json.loads(metadata)['data']['attributes']
    add_metadata(container,metadata,'deffile')
    add_metadata(container,metadata,'runscript')
    add_metadata(container,metadata,'test')
    add_metadata(container,metadata,'environment')

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
    if metadata['labels'] not in [None,'']:
        container = update_container_labels(container,metadata['labels'])

    container.save()
