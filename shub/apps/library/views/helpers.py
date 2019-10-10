'''

Copyright (C) 2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from shub.apps.main.views import get_collection_named
from rest_framework.authtoken.models import Token
from shub.apps.users.models import User
from shub.apps.main.models import Collection

# shared date time format string
formatString = '%Y-%m-%dT%X.%fZ'

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
            'id': user.id,
            'name': user.username,
            'description': user.username,
            'size': 0,
            'quota': 0,
            'defaultPrivate': False,
            'customData': ''}

    return data


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
    '''given a collection, generate a metadata response for it.
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

    metadata = {'containers': containers,
                'createdAt': '2019-04-02T19:46:45.316Z',
                'createdBy': '5bb3c5366cf09e000197a5ed',
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

    return metadata


def get_container(names):
    '''a helper function to take a parsed uri names, and return
       an associated container
    '''
    container = None

    try:
        collection = get_collection_named(names['url'])
    except:
        collection = None

    # If we have a collection, next look for the tag or version
    if collection is not None:
        container = collection.containers.filter(tag=names['tag']).first()
        if container is None:
            container = collection.containers.filter(version=names['version']).first()

    return container
