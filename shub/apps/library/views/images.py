'''

Copyright (C) 2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from django.conf import settings
from django.shortcuts import (
    redirect,
    reverse
)
from sregistry.utils import parse_image_name

from shub.apps.logs.models import APIRequestCount
from shub.apps.main.models import Collection

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer

from .helpers import (
    generate_collections_list,
    generate_collection_metadata,
    get_token,
    get_container,
    validate_token
)


class DownloadImageView(APIView):
    '''redirect to the url to download a container.
       https://library.sylabs.io/v1/imagefile/busybox:latest
    '''
    def get_download_url(self, container):

        if "image" in container.metadata:
            return container.metadata['image']
                
        secret = container.collection.secret
        url = reverse('download_container', kwargs={'cid':container.id,
                                                     'secret':secret})
        return "%s%s" %(settings.DOMAIN_NAME, url)

    def get(self, request, name):
        names = parse_image_name(name)
        container = get_container(names)

        # Does it come with headers?
        print(request.META)

        # TODO: need to check permissions here
        # TODO: what to return when can't find container?
        if container is None:
            return Response(status=404)

        # Private containers are simply not accessible - no way to authenticate
        if container.collection.private:
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

        # Private containers are simply not accessible - no way to authenticate
        if container.collection.private:
            return Response(status=404)

        # Get other tags
        tags = [c.tag for c in container.collection.containers.all()]

        # Downloads
        path = "images/%s/%s:%s" %(names['collection'], names['image'], names['tag']) 
        downloads = APIRequestCount.objects.filter(method="get", path__contains=path).count()

        data = {"deleted": False,                        # 2019-03-15T19:02:24.015Z
                "createdAt": container.add_date.strftime('%Y-%m-%dT%H:%M:%S.%jZ'), # No idea what their format is...
                "hash": container.version,
                "size": container.metadata.get('size_mb'),
                "entityName": container.name,
                "collectionName": container.collection.name.split('/')[0],
                "containerName": container.name.split('/')[0],
                "tags": tags,
                "containerStars": container.collection.star_set.count(),
                "containerDownloads": downloads}

        return Response(data={"data": data}, status=200)


#TODO: this need ratelimit added (or is already present from django restful?)

class CollectionsView(APIView):
    '''Return a simple list of collections
       GET /v1/collections
    '''
    renderer_classes = (JSONRenderer,)

    def get(self, request):

        print(request.data)
        if not validate_token(request):
            print("Token not valid")
            return Response(status=404)

        token = get_token(request)
        collections = generate_collections_list(token.user)
        return Response(data=collections, status=200)


class GetNamedCollectionView(APIView):
    '''Given a collection, return the associated metadata.
       GET /v1/collections/<username>/<name>
    '''
    renderer_classes = (JSONRenderer,)

    def get(self, request, username, name):

        if not validate_token(request):
            print("Token not valid")
            return Response(status=404)

        # The user is associated with the token
        token = get_token(request)

        # Look up the collection
        try:
            collection = Collection.objects.get(name=name)
        except Collection.DoesNotExist:
            return Response(status=404)        

        if token.user in collection.owners.all():
            metadata = generate_collection_metadata(collection, token.user)
            return Response(data={"data": metadata}, status=200)
        return Response(status=404)
