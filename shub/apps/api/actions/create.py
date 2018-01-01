'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017 Vanessa Sochat.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

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
