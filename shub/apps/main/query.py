"""

Copyright (C) 2017-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""


from shub.apps.main.models import Container, Collection
from sregistry.utils import parse_image_name
from django.db.models import Q


def collection_query(q):
    return Collection.objects.filter(
        Q(name__contains=q)
        | Q(containers__name__contains=q)
        | Q(containers__tags__name__contains=q)
        | Q(containers__tag__contains=q)
    ).distinct()


def container_query(q, across_collections=1):
    """query for a container depending on the provided query string"""
    across_collections = bool(int(across_collections))

    # Return complete lookup with image, collection, tag
    q = parse_image_name(q, defaults=False)

    if across_collections:
        if q["tag"] is not None:

            # Query across collections for image name and tag
            return Container.objects.filter(
                Q(name__contains=q["image"]) | Q(tag__contains=q["tag"])
            ).distinct()

        # Query across collections for image name
        return Container.objects.filter(Q(name__contains=q["image"])).distinct()

    # Query a particular collection for image name and tag
    if q["tag"] is not None:
        return Collection.objects.filter(
            Q(name__contains=q["image"])
            | Q(collection__name__contains=q["collection"])
            | Q(containers_tags__contains=q["tag"])
        ).distinct()

    # Query a particular collection for image name
    return Collection.objects.filter(
        Q(name__contains=q["image"]) | Q(collection__name__contains=q["collection"])
    ).distinct()


def specific_container_query(name, collection=None, tag=None):
    """single container query is intended to return a queryset when a specific collection and
       container name is asked for.
    """
    if collection is not None:
        collection = collection.lower()
    if name is not None:
        name = name.lower()
    if tag is not None:
        tag = tag.lower()

    if tag is None and collection is None and name is None:
        return Container.objects.all()

    if tag is None and collection is None:
        return Container.objects.filter(name=name)

    if tag is None:
        return Container.objects.filter(collection__name=collection, name=name)

    if collection is None:
        return Container.objects.filter(tag=tag, name=name)
    return Container.objects.filter(collection__name=collection, name=name, tag=tag)


def container_lookup(collection, name, tag=None, return_collection=False):
    """container lookup will parse a query string from the url to look up
       a container. If lookup incorrect or no container
       is found, None is returned.

       Parameters
       ==========
    collection: the name of the collection
    name: the name of the container
    tag: the name of the tag. Defaults to latest

    """
    if tag is None:
        tag = "latest"

    tag = tag.lower()
    name = name.lower()
    collection = collection.lower()

    container = None
    contenders = Container.objects.filter(
        name=name, tag=tag, collection__name=collection
    )

    # If no contenders, try sending most recent tag
    if not contenders:
        contenders = Container.objects.filter(name=name, collection__name=collection)

    if not contenders:
        return container  # No contenders, return None

    container = contenders.last()

    if return_collection and container is not None:
        return container.collection

    return container
