'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from itertools import chain
from django.http import HttpRequest
import os

def has_edit_permission(instance, request):
    '''can the user of the request edit the collection or container?

       Parameters
       ==========
       instance: the container or collection to check
       request: the request with the user object OR the user object

    '''
    if isinstance(instance, Container):
        instance = instance.collection

    user = request
    if isinstance(user, HttpRequest):
        user = request.user

    # Visitor
    if not user.is_authenticated:
        return False

    # Global Admins
    if user.is_staff:
        return True

    if user.is_superuser:
        return True

    # Collection Owners can edit
    if user in instance.owners.all():
        return True
    return False


def has_view_permission(instance, request):
    '''can the user of the request view the collection or container? This
       permission corresponds with being a contributor, and being able to
       pull

       Parameters
       ==========
       instance: the container or collection to check
       request: the request with the user object

    '''
    if isinstance(instance, Container):
        instance = instance.collection

    user = request
    if isinstance(user, HttpRequest):
        user = request.user

    # All public collections are viewable
    if instance.private is False:
        return True

    # At this point we have a private collection
    if not user.is_authenticated:
        return False
        
    # Global Admins and Superusers
    if user.is_staff or user.is_superuser:
        return True

    # Collection Contributors (owners and contributors)
    contributors = instance.members()
    if user in contributors:
        return True

    return False


def get_collection_users(instance):
    '''get_collection_users will return a list of all owners and contributors
        for a collection. The input instance can be a collection or container.

        Parameters
        ==========
        instance: the collection or container object to use

    '''
    collection = instance
    if isinstance(collection, Container):
        collection = collection.collection

    contributors = collection.contributors.all()
    owners = collection.owners.all()
    members = list(chain(contributors, owners))
    return list(set(members))


