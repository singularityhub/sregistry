'''

Copyright (C) 2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from shub.apps.logs.models import APIRequestCount
from rest_framework.authtoken.models import Token
from shub.apps.users.models import User
from shub.apps.main.models import Collection

import re

# shared date time format string
formatString = '%Y-%m-%dT%X.%fZ'


# Tokens 

def validate_token(request):
    '''validate a token from the request header. If valid, return
       True. Otherwise return False
    '''
    token = request.META.get("HTTP_AUTHORIZATION")

    if token:
        try:
            Token.objects.get(key=token.replace("BEARER", "").strip())
            return True
        except Token.DoesNotExist:
            pass
    return False


def get_token(request):
    '''The same as validate_token, but return the token object to check the
       associated user.
    '''
    token = request.META.get("HTTP_AUTHORIZATION")

    if token:
        try:
            return Token.objects.get(key=token.replace("BEARER", "").strip())
        except Token.DoesNotExist:
            pass


# Downloads


def get_collection_downloads(collection):
    '''get downloads for a collection (downloads for all containers within)
    '''
    downloads = 0
    for container in collection.containers.all():
        downloads += get_container_downloads(container)
    return 


def get_container_downloads(container):
    '''return downloads for a container
    '''
    path = "images/%s/%s:%s" %(container.collection.name, container.name, container.tag) 
    return APIRequestCount.objects.filter(method="get", path__contains=path).count()



# Users

def generate_user_data(user):
    '''for the entity/entities endpoint, we send back dummy data about the user
    '''
    # Owned collections
    collections = Collection.objects.filter(owners=user)

    # Generate dummy data about user
    data = {'collections': [str(c.id) for c in collections],
            'deleted': not user.active,
            'createdBy': '',
            'createdAt': user.date_joined.strftime(formatString),
            'updatedBy': '',
            'updatedAt': user.last_login.strftime(formatString),
            'deletedAt': '0001-01-01T00:00:00Z',
            'id': str(user.id),
            'name': user.username,
            'description': user.username,
            'size': 0,
            'quota': 0,
            'defaultPrivate': False,
            'customData': ''}

    return data


# Collections


def generate_collections_list(user):
    '''generate a list of collections, only done if the user is authenticated.
       we take the user as argument, and return private collections for him
       or her.
    '''
    collections = []
    for collection in Collection.objects.all(): 

        metadata = generate_collection_metadata(collection)
        collections.append(metadata)
        return {"collections": collections}


def generate_collection_metadata(collection, user=None):
    '''given a collection, generate a metadata response for it. This does
       not include metadata about container tag 
       (see generate_collection_containers_metadata)
    '''
    if not user:
        user = collection.owners.first()

    # Sylabs listing is inconsistent between None and []
    containers = []
    if not collection.private:
        containers = collection.containers.all() or []

    # Only owners can see private containers
    elif collection.private and user in collection.owners.all():
        containers = collection.containers.all() or []

    # Only need the ids, but as strings
    containers = [str(c.id) for c in containers]

    data = {'containers': containers,
            'createdAt': collection.add_date.strftime(formatString),
            'createdBy': str(collection.owners.first().id),
            'customData': '',
            'deleted': False, # never going to be True :)
            'deletedAt': '0001-01-01T00:00:00Z',
            'description': "%s Collection" % collection.name.capitalize(),
            'entity': str(user.id),
            'entityName': user.username,
            'id': str(collection.id),
            'name': collection.name,
            'owner': str(user.id),
            'private': collection.private,
            'size': collection.containers.count(), # Possibly MB?
            'updatedAt': collection.modify_date.strftime(formatString),
            'updatedBy': str(user.id)}

    return data


def generate_collection_details(collection, containers, user=None):
    '''given a collection, generate complete metadata for it, including
       a list of all associated tags. For Sylabs Cloud, although the
       request may target a specific container:

       https://library.sylabs.io/v1/containers/dtrudg/linux/ubuntu

       For Singularity Registry server, this means filtering containers in
       a collection (e.g., linux) down to a submit (e.g., ubuntu) and
       then returning the corresponding tags (e.g., 14.04).
    ''' 
    if not user:
        user = collection.owners.first()

    tags = {}
    name = ""
    for container in containers:
        name = container.name
        tags[container.tag] = str(container.id)

    images = [c.version for c in containers]
    data = generate_collection_metadata(collection, user)

    updates = {'archTags': {'amd64': tags },
               'collection': str(collection.id),
               'collectionName': collection.name,
               'downloadCount': get_collection_downloads(collection),
               'fullDescription': data.get('description', ''),
               'imageTags': tags,
               'images': images,
               'readOnly': False,
               'stars': collection.star_set.count()}

    data.update(updates)
    return data



# Containers

def generate_container_metadata(container):
    '''given a container, return a metadata object
    '''
    # Get other tags
    tags = [c.tag for c in container.collection.containers.all()]

    # Downloads
    downloads = get_container_downloads(container)

    # Container name might have /
    container_name = container.name
    collection_name = container.collection.name
    if "/" in container_name:
        container_name = container_name.split('/')[-1]

    if "/" in collection_name:
        collection_name = collection_name.split("/")[0]

    data = {"deleted": False,                        # 2019-03-15T19:02:24.015Z
            "createdAt": container.add_date.strftime(formatString), # No idea what their format is...
            "createdBy": str(container.collection.owners.first().id),
            "createdAt": container.add_date.strftime(formatString), # No idea what their format is...
            "updatedBy": str(container.collection.owners.first()),
            "owner": str(container.collection.owners.first().id),
            "id": str(container.id),
            "hash": container.version,
            "description": "%s Collection" % container.collection.name.capitalize(),
            "container": container.version,
            "arch": "amd64",
            "fingerprints": [],
            "customData": "",
            "size": container.metadata.get('size_mb'),
            "entity": str(container.collection.owners.first().id),
            "entityName": container.collection.owners.first().username,
            "collection": str(container.collection.id),
            "collectionName": collection_name,
            "containerName": container_name,
            "tags": tags,
            "containerStars": container.collection.star_set.count(),
            "containerDownloads": downloads}

    return data


def get_container(names):
    '''a helper function to take a parsed uri names, and return
       an associated container
    '''
    container = None

    # The user can provide the username (a username) that owns the container
    # We don't actually need it - namespace doesn't include username
    if names['registry']:
        if names['registry'] in names['url']:
            names['url'] = re.sub('^%s/' % names['registry'], '', names['url'])

    collection = get_collection(names['url'])
    print(collection)

    # If we have a collection, next look for the tag or version
    if collection is not None:
        container = collection.containers.filter(tag=names['tag']).first()
        if container is None:
            container = collection.containers.filter(version=names['version']).first()

    return container


def get_collection(name, retry=True):
    '''get a collection by name. First we try the collection name,
       then we try splitting if the name includes /

       Parameters
       ==========
       name: the name of the collection to look up
    '''
    try:
        collection = Collection.objects.get(name=name)
        return collection
    except Collection.DoesNotExist:
        if retry is True and "/" in name:
            name = name.split('/')[0]
            return get_collection(name, retry=False)
