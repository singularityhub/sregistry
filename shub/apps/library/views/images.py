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

from shub.apps.logs.utils import generate_log
from shub.apps.main.models import (
    Collection, 
    Container
)

from ratelimit.mixins import RatelimitMixin

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer

from .helpers import (
    formatString,
    generate_collections_list,
    generate_collection_details, # includes containers
    generate_collection_metadata,
    generate_container_metadata,
    get_token,
    get_container,
    validate_token
)

import django_rq
import uuid

class PushImageFileView(RatelimitMixin, GenericAPIView):
    '''After creating the container, push the image file. Still check
       all credentials!
    '''
    renderer_classes = (JSONRenderer,)
    ratelimit_key = 'ip'
    ratelimit_rate = settings.VIEW_RATE_LIMIT 
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = 'GET'
    renderer_classes = (JSONRenderer,)

    def post(self, request, container_id):

        print("POST PushImageFileView")
        print(container_id)
        print(request.META)
        print(request.data)
        print(request.FILES)

        if not validate_token(request):
            print("Token not valid")
            return Response(status=404)

        token = get_token(request)

       # STOPPED HERE - request.META has wsgi.file_wrapper that we should be able
       # to stream to file?
              
# uwsgi_1_f2461bcb4d31 | {'wsgi.url_scheme': 'http', 'SERVER_PROTOCOL': 'HTTP/1.1', 'REMOTE_ADDR': '172.17.0.1', 'wsgi.file_wrapper': <built-in function uwsgi_sendfile>, 'DOCUMENT_ROOT': '/etc/nginx/html', 'wsgi.errors': <_io.TextIOWrapper name=2 mode='w' encoding='UTF-8'>, 'SERVER_NAME': 'localhost', 'HTTP_ACCEPT_ENCODING': 'gzip', 'uwsgi.version': b'2.0.18', 'SCRIPT_NAME': '', 'HTTP_USER_AGENT': 'Go-http-client/1.1', 'wsgi.multiprocess': True, 'HTTP_AUTHORIZATION': 'BEARER xxxxxxxxxxxx', 'uwsgi.node': b'40e6429d3b61', 'REQUEST_METHOD': 'POST', 'wsgi.version': (1, 0), 'REQUEST_URI': '/v2/imagefile/9', 'HTTP_CONTENT_LENGTH': '63', 'wsgi.input': <uwsgi._Input object at 0x7f68374d8a08>, 'SERVER_PORT': '80', 'QUERY_STRING': '', 'wsgi.multithread': True, 'CONTENT_TYPE': '', 'REMOTE_PORT': '60666', 'CONTENT_LENGTH': '63', 'uwsgi.core': 1, 'HTTP_HOST': '127.0.0.1', 'wsgi.run_once': False, 'PATH_INFO': '/v2/imagefile/9'}
# uwsgi_1_f2461bcb4d31 | Unsupported Media Type: /v2/imagefile/9

        # Look up the collection
        try:
            container = Container.objects.get(id=container_id)
        except Container.DoesNotExist:
            return Response(status=404)        
        
        if token.user not in container.collection.owners():
            return Response(status=403)  



class PushImageView(RatelimitMixin, GenericAPIView):
    '''Given a collection and container name, return the associated metadata.
       GET /v1/containers/vsoch/dinosaur-collection/container
    '''
    renderer_classes = (JSONRenderer,)
    ratelimit_key = 'ip'
    ratelimit_rate = settings.VIEW_RATE_LIMIT 
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = 'GET'
    renderer_classes = (JSONRenderer,)

    def get(self, request, username, collection, name, version):

        print("GET PushNamedContainerView")

        if not validate_token(request):
            print("Token not valid")
            return Response(status=404)

        token = get_token(request)

        # Look up the collection
        try:
            collection = Collection.objects.get(name=collection)
        except Collection.DoesNotExist:
            return Response(status=404)        

        if token.user not in collection.owners.all():
            return Response(status=403)  

        # We have to generate a temporary tag, or it will overwrite latest
        tag = str(uuid.uuid4())

        container, created = Container.objects.get_or_create(collection=collection,
                                                             name=name,
                                                             tag=tag,
                                                             version=version)
        print(container)
        print(created)

        arch = request.query_params.get('arch')
        if arch:
            container.metadata['arch'] = arch

        data = generate_container_metadata(container)
        return Response(data={"data": data}, status=200)


class DownloadImageView(RatelimitMixin, GenericAPIView):
    '''redirect to the url to download a container.
       https://library.sylabs.io/v1/imagefile/busybox:latest
       I'm not actually sure if this view is being used anymore.
    '''

    ratelimit_key = 'ip'
    ratelimit_rate = settings.VIEW_RATE_LIMIT 
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = 'GET'

    def get_download_url(self, container):

        if "image" in container.metadata:
            return container.metadata['image']
                
        secret = container.collection.secret
        url = reverse('download_container', kwargs={'cid':container.id,
                                                    'secret':secret})
        return "%s%s" %(settings.DOMAIN_NAME, url)

    def get(self, request, name):
        print("GET DownloadImageView")
        print(request.query_params)
        names = parse_image_name(name)
        container = get_container(names)

        # If no container, regardles of permissions, 404
        if container is None:
            return Response(status=404)

        # Private containers we check the token
        if container.collection.private:
            token = get_token(request)

            # Only owners and contributors can pull
            collection = container.collection
            if token.user not in collection.owners.all() and token.user not in collection.contributors.all():
                return Response(status=404)

        return redirect(self.get_download_url(container))

#TODO can we get arch or fingerprint from push?
#TODO need to check how generating download counts (not working)


class GetImageView(RatelimitMixin, GenericAPIView):
    '''redirect to the url to download a container.
       https://library.sylabs.io/v1/imagefile/busybox:latest
    '''
    renderer_classes = (JSONRenderer,)
    ratelimit_key = 'ip'
    ratelimit_rate = settings.VIEW_RATE_LIMIT 
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = 'GET'

    def get(self, request, name):

        # The request specifies ?arch=amd64 but that's all we got
        print("GET GetImageView")

        print(name)
        names = parse_image_name(name)
        print(names)

        # The user can specify an arch, currently only support amd64
        arch = request.query_params.get('arch')
        if arch:
            if arch != "amd64":
                return Response(status=404)
    
        container = get_container(names)

        # If no container, regardles of permissions, 404
        if container is None:
            return Response(status=404)

        # Private containers we check the token
        if container.collection.private:
            token = get_token(request)

            # Only owners and contributors can pull
            collection = container.collection
            if token.user not in collection.owners.all() and token.user not in collection.contributors.all():
                return Response(status=404)

        # Generate log for downloads (async with worker)
        django_rq.enqueue(generate_log,
                          view_name = 'shub.apps.api.urls.containers.ContainerDetailByName',
                          ipaddr = request.META.get("HTTP_X_FORWARDED_FOR", None),
                          method = request.method,
                          params = request.query_params.dict(),
                          request_path = request.path,
                          remote_addr = request.META.get("REMOTE_ADDR", ""),
                          host = request.get_host(),
                          request_data = request.data,
                          auth_header = request.META.get("HTTP_AUTHORIZATION"))

        data = generate_container_metadata(container)
        return Response(data={"data": data}, status=200)


# Collections

class CollectionsView(RatelimitMixin, GenericAPIView):
    '''Return a simple list of collections
       GET /v1/collections
    '''
    renderer_classes = (JSONRenderer,)
    ratelimit_key = 'ip'
    ratelimit_rate = settings.VIEW_RATE_LIMIT 
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = 'GET'
    renderer_classes = (JSONRenderer,)

    def get(self, request):

        print("GET CollectionsView")
        print(request.query_params)
        print(request.data)
        if not validate_token(request):
            print("Token not valid")
            return Response(status=404)

        token = get_token(request)
        collections = generate_collections_list(token.user)
        return Response(data=collections, status=200)


class ContainersView(RatelimitMixin, GenericAPIView):
    '''Return a simple list of containers
       GET /v1/containers
    '''
    renderer_classes = (JSONRenderer,)
    ratelimit_key = 'ip'
    ratelimit_rate = settings.VIEW_RATE_LIMIT 
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = 'GET'
    renderer_classes = (JSONRenderer,)

    def get(self, request):

        print("GET ContainersView")
        print(request.data)
        print(request.query_params)
        if not validate_token(request):
            print("Token not valid")
            return Response(status=404)

        token = get_token(request)
        #collections = generate_collections_list(token.user)
        return Response(data={}, status=200)


class GetNamedCollectionView(RatelimitMixin, GenericAPIView):
    '''Given a collection, return the associated metadata.
       We don't care about the username, but Singularity push requires it.
       GET /v1/collections/<username>/<name>
    '''
    renderer_classes = (JSONRenderer,)
    ratelimit_key = 'ip'
    ratelimit_rate = settings.VIEW_RATE_LIMIT 
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = 'GET'
    renderer_classes = (JSONRenderer,)

    def get(self, request, name, username=None):

        print("GET GetNamedCollectionView")

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
            details = generate_collection_metadata(collection, token.user)
            return Response(data={"data": details}, status=200)
        return Response(status=404)


# Containers


class GetNamedContainerView(RatelimitMixin, GenericAPIView):
    '''Given a collection and container name, return the associated metadata.
       GET /v1/containers/vsoch/dinosaur-collection/container
    '''
    renderer_classes = (JSONRenderer,)
    ratelimit_key = 'ip'
    ratelimit_rate = settings.VIEW_RATE_LIMIT 
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = 'GET'
    renderer_classes = (JSONRenderer,)

    def get(self, request, username, name, container):

        print("GET GetNamedContainerView")

        # WHERE IS THE TAG?
        print(request.query_params)
        print(username)
        print(name)
        print(container)

        if not validate_token(request):
            print("Token not valid")
            return Response(status=404)

        # The user is associated with the token
        token = get_token(request)

        # Look up the collection first
        try:
            collection = Collection.objects.get(name=name)
        except Collection.DoesNotExist:
            return Response(status=404)        

        # If not an owner, denied
        if token.user not in collection.owners.all():
            return Response(status=403)

        # We don't need to create the specific container here
        containers = collection.containers.filter(name=container) or []
 
        if not containers:
            return Response(status=404)

        data = generate_collection_details(collection, containers, token.user)
        return Response(data={"data": data}, status=200)
