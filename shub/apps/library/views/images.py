'''

Copyright (C) 2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from django.conf.urls import url
from django.http import Http404
from django.shortcuts import (
    redirect,
    reverse
)
from sregistry.utils import parse_image_name
import os

from shub.apps.logs.models import APIRequestCount
from shub.apps.api.utils import ObjectOnlyPermissions
from shub.apps.main.models import Container, Collection
from shub.apps.main.views import get_collection_named

from django.conf import settings

from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer


def get_container(names):
    '''a helper function to take a parsed uri names, and return
       an associated container
    '''
    container = None

    try:
        collection = get_collection_named(names['collection'])
    except:
        collection = None

    # If we have a collection, next look for the tag or version
    if collection is not None:
        container = collection.containers.filter(tag=names['tag']).first()
        if container is None:
            container = collection.containers.filter(version=names['version']).first()

    return container


class DownloadImageView(APIView):
    '''redirect to the url to download a container.
       https://library.sylabs.io/v1/imagefile/busybox:latest
    '''
    def get_download_url(self, container):

        if "image" in container.metadata:
            return container.metadata['image']
                
        secret = container.collection.secret
        url = reverse('download_container', kwargs= {'cid':container.id,
                                                     'secret':secret})
        return "%s%s" %(settings.DOMAIN_NAME, url)

    def get(self, request, name):
        names = parse_image_name(name)
        container = get_container(names)

        # TODO: need to check permissions here
        # TODO: what to return when can't find container?
        if container is None:
            return Response(status=404)

        return redirect(self.get_download_url(container))


class GetImageView(APIView):
    '''Get a manifest will retrieve an image manifest for a particular image
       name and tag uri / digest (the reference).
       https://github.com/opencontainers/image-spec/blob/master/manifest.md

       GET /v2/<name>/manifests/<reference>
    '''
    renderer_classes = (JSONRenderer,)

    def get(self, request, name):
        names = parse_image_name(name)
        container = get_container(names)

        # TODO: need to check permissions here
        # TODO: what to return when can't find container?
        if container is None:
            return Response(status=404)

        # Get other tags
        tags = [c.tag for c in container.collection.containers.all()]

        # Downloads
        path = "images/%s/%s:%s" %(names['collection'], names['image'], names['tag']) 
        downloads = APIRequestCount.objects.filter(method="get", path__contains=path).count()

        data = {"deleted": False,
                "createdAt": container.add_date.strftime('%Y-%m-%dT%H:%M:%S%z'),    
                "hash": container.version,
                "size": container.metadata.get('size_mb'),
                "entityName": container.name,
                "collectionName": container.collection.name.split('/')[0],
                "containerName": container.name.split('/')[0],
                "tags": tags,
                "containerStars": container.collection.star_set.count(),
                "containerDownloads": downloads}

        return Response(data=data, status=200)
