"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.shortcuts import redirect, reverse
from sregistry.utils import parse_image_name

from shub.apps.logs.utils import generate_log
from shub.apps.main.models import Collection, Container

from ratelimit.mixins import RatelimitMixin

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer

from .parsers import OctetStreamParser, EmptyParser

from .helpers import (
    formatString,
    generate_collection_tags,
    generate_collections_list,
    generate_collection_details,  # includes containers
    generate_collection_metadata,
    generate_container_metadata,
    get_token,
    get_container,
    validate_token,
)

import django_rq
import shutil
import tempfile
import json
import uuid
import os
import random
import string

# regarding remote build singularity spec is send to library as binary.
# So we need go unmarshal to it
from ctypes import *

lib = cdll.LoadLibrary("/code/lib/unmarshal.so")

class GoString(Structure):
    _fields_ = [("p", c_char_p), ("n", c_longlong)]

lib.Unmarshal.argtypes = [GoString, GoString]
lib.Unmarshal.restype = int


# Image Files


class CompletePushImageFileView(RatelimitMixin, APIView):
    """This view (UploadImageCompleteRequest) isn't currently useful,
       but should exist as it is used for Singularity.
    """

    ratelimit_key = "ip"
    ratelimit_rate = settings.VIEW_RATE_LIMIT
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = "PUT"
    renderer_classes = (JSONRenderer,)
    parser_classes = (EmptyParser,)

    def put(self, request, container_id, format=None):

        print("PUT CompletePushImageFileView")

        try:
            container = Container.objects.get(id=container_id)
            print(container.tag)
            return Response(status=200)
        except Container.DoesNotExist:
            return Response(status=404)


class RequestPushImageFileView(RatelimitMixin, APIView):
    """After creating the container, push the image file. Still check
       all credentials!
    """

    ratelimit_key = "ip"
    ratelimit_rate = settings.VIEW_RATE_LIMIT
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = "POST"
    renderer_classes = (JSONRenderer,)

    def post(self, request, container_id, format=None):

        print("POST RequestPushImageFileView")

        if not validate_token(request):
            print("Token not valid")
            return Response(status=404)

        # Look up the container to set a temporary upload secret
        try:
            container = Container.objects.get(id=container_id)
        except Container.DoesNotExist:
            return Response(status=404)

        # check user permission
        token = get_token(request)
        if token.user not in container.collection.owners.all():
            return Response(status=403)

        push_secret = str(uuid.uuid4())
        container.metadata["pushSecret"] = push_secret
        container.save()

        # TODO this could check for Google Build, and return signed upload URL, or S3 signed URL
        url = settings.DOMAIN_NAME + reverse(
            "PushImageFileView", args=[str(container_id), push_secret]
        )

        data = {"uploadURL": url}
        return Response(data={"data": data}, status=200)


class PushImageFileView(RatelimitMixin, APIView):
    """After creating the container, push the image file. Still check
       all credentials!
    """

    ratelimit_key = "ip"
    ratelimit_rate = settings.VIEW_RATE_LIMIT
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = "PUT"
    renderer_classes = (JSONRenderer,)
    parser_classes = (OctetStreamParser,)

    def put(self, request, container_id, secret, format=None):

        print("PUT PushImageFileView")

        # Look up the container
        try:
            container = Container.objects.get(id=container_id)
        except Container.DoesNotExist:
            return Response(status=404)

        # The secret must match the one just generated for the URL
        if container.metadata.get("pushSecret", "nope") != secret:
            return Response(status=403)
        del container.metadata["pushSecret"]

        # Create collection root, if it doesn't exist
        image_home = "%s/%s" % (settings.MEDIA_ROOT, container.collection.name)
        if not os.path.exists(image_home):
            os.mkdir(image_home)

        # Write the file to location
        from shub.apps.api.models import ImageFile

        suffix = next(tempfile._get_candidate_names())
        container_path = os.path.join(
            image_home, "%s-%s-%s.sif" % (container.name, container.version, suffix)
        )
        final_container_path = os.path.join(
            image_home, "%s-%s.sif" % (container.name, container.version)
        )
        file_obj = request.data["file"]

        with default_storage.open(container_path, "wb+") as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)

        # Save newly uploaded file to model
        reopen = open(container_path, "rb")
        django_file = File(reopen)

        # If the final path exists, remove it
        if os.path.exists(final_container_path):
            os.remove(final_container_path)

        # If there is a container file already existing, use it
        try:
            imagefile = ImageFile.objects.get(
                collection=container.collection.name, name=container_path
            )
        except ImageFile.DoesNotExist:
            imagefile = ImageFile.objects.create(
                collection=container.collection.name, name=container_path
            )

        imagefile.datafile.save(final_container_path, django_file, save=True)
        shutil.move(container_path, final_container_path)
        container.image = imagefile
        container.save()
        return Response(status=200)


class PushImageView(RatelimitMixin, APIView):
    """Given a collection and container name, return the associated metadata.
       GET /v1/containers/vsoch/dinosaur-collection/container
    """

    renderer_classes = (JSONRenderer,)
    ratelimit_key = "ip"
    ratelimit_rate = settings.VIEW_RATE_LIMIT
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = "GET"
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
        tag = "DUMMY-%s" % str(uuid.uuid4())

        # The container will always be created, and it needs to be handled later
        container, created = Container.objects.get_or_create(
            collection=collection,
            name=name,
            frozen=False,
            tag=tag,
            version="sha256." + version,
        )
        arch = request.query_params.get("arch")
        if arch:
            container.metadata["arch"] = arch

        data = generate_container_metadata(container)
        return Response(data={"data": data}, status=200)


class DownloadImageView(RatelimitMixin, APIView):
    """redirect to the url to download a container.
       https://library.sylabs.io/v1/imagefile/busybox:latest
       I'm not actually sure if this view is being used anymore.
    """

    ratelimit_key = "ip"
    ratelimit_rate = settings.VIEW_RATE_LIMIT
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = "GET"

    def get_download_url(self, container):

        if "image" in container.metadata:
            return container.metadata["image"]

        secret = container.collection.secret
        url = reverse(
            "download_container", kwargs={"cid": container.id, "secret": secret}
        )
        return "%s%s" % (settings.DOMAIN_NAME, url)

    def get(self, request, name):
        print("GET DownloadImageView")
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
            if (
                token.user not in collection.owners.all()
                and token.user not in collection.contributors.all()
            ):
                return Response(status=404)

        return redirect(self.get_download_url(container))


class GetImageView(RatelimitMixin, APIView):
    """redirect to the url to download a container.
       https://library.sylabs.io/v1/imagefile/busybox:latest
    """

    renderer_classes = (JSONRenderer,)
    ratelimit_key = "ip"
    ratelimit_rate = settings.VIEW_RATE_LIMIT
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = "GET"

    def get(self, request, name):

        # The request specifies ?arch=amd64 but that's all we got
        print("GET GetImageView")
        names = parse_image_name(name)

        # If an arch is not specified, redirect to push view
        arch = request.query_params.get("arch", "amd64")

        container = get_container(names)

        # If an arch is defined, ensure it matches the request
        arch = "amd64"
        if arch and container is not None:
            if container.metadata.get("arch", "amd64") != "amd64":
                return Response(status=404)

        # If no container, regardles of permissions, 404
        if container is None:
            return Response(status=404)

        # Private containers we check the token
        if container.collection.private:
            token = get_token(request)

            # Only owners and contributors can pull
            collection = container.collection
            if (
                token.user not in collection.owners.all()
                and token.user not in collection.contributors.all()
            ):
                return Response(status=404)

        # Generate log for downloads (async with worker)
        django_rq.enqueue(
            generate_log,
            view_name="shub.apps.api.urls.containers.ContainerDetailByName",
            ipaddr=request.META.get("HTTP_X_FORWARDED_FOR", None),
            method=request.method,
            params=request.query_params.dict(),
            request_path=request.path,
            remote_addr=request.META.get("REMOTE_ADDR", ""),
            host=request.get_host(),
            request_data=request.data,
            auth_header=request.META.get("HTTP_AUTHORIZATION"),
        )

        data = generate_container_metadata(container)
        return Response(data={"data": data}, status=200)


# Collections


class CollectionsView(RatelimitMixin, APIView):
    """Return a simple list of collections
       GET /v1/collections
    """

    ratelimit_key = "ip"
    ratelimit_rate = settings.VIEW_RATE_LIMIT
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = "GET"
    renderer_classes = (JSONRenderer,)

    def get(self, request):

        print("GET CollectionsView")
        if not validate_token(request):
            print("Token not valid")
            return Response(status=404)

        token = get_token(request)
        collections = generate_collections_list(token.user)
        return Response(data=collections, status=200)


class GetCollectionTagsView(RatelimitMixin, APIView):
    """Return a simple list of tags in the collection, and the
       containers associated with. Since we can only return one container
       per tag, we take the most recently created. This means that
       not all container ids will be returned for any given tag.
       GET /v1/tags/<collection_id>
    """

    ratelimit_key = "ip"
    ratelimit_rate = settings.VIEW_RATE_LIMIT
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = ("GET", "POST")
    renderer_classes = (JSONRenderer,)
    parser_classes = (EmptyParser,)

    def get(self, request, collection_id):

        print("GET CollectionTagsView")
        if not validate_token(request):
            print("Token not valid")
            return Response(status=404)

        try:
            collection = Collection.objects.get(id=collection_id)
        except:
            return Response(status=404)

        # Always return empty so it hits the container tag generation endpoint
        tags = generate_collection_tags(collection)
        return Response(data={"data": tags}, status=200)

    def post(self, request, collection_id):

        print("POST ContainerTagView")

        if not validate_token(request):
            print("Token not valid")
            return Response(status=404)

        # {'Tag': 'latest', 'ImageID': '60'}
        params = json.loads(request.data.decode("utf-8"))

        # We can only get the image name based on the container here
        try:
            container = Container.objects.get(id=params["ImageID"])
        except Container.DoesNotExist:
            return Response(status=404)

        selected = None

        try:
            # First try - get container with already existing tag
            existing = Container.objects.get(name=container.name, tag=params["Tag"])

        except Container.DoesNotExist:
            existing = None

        # If the container is existing and frozen, no go.
        if existing is not None:

            # Case 1: the tag exists, and it's frozen
            if existing.frozen:

                # We can't create this new container with the tag, delete it
                container.image = None
                container.save()
                container.delete()
                return Response(
                    {"message": "This tag exists, and is frozen."}, status=400
                )

            # Case 2: Exists and not frozen (replace)
            container.image = None
            container.save()
            container.delete()
            selected = existing

        # Not existing, our container is selected for the tag
        else:
            selected = container

        # Apply the tag and save!
        selected.tag = params["Tag"]
        selected.save()
        return Response(status=200)


# Containers


class ContainersView(RatelimitMixin, APIView):
    """Return a simple list of containers
       GET /v1/containers
    """

    renderer_classes = (JSONRenderer,)
    ratelimit_key = "ip"
    ratelimit_rate = settings.VIEW_RATE_LIMIT
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = "GET"
    renderer_classes = (JSONRenderer,)

    def get(self, request):

        print("GET ContainersView")
        print(request.data)
        print(request.query_params)
        if not validate_token(request):
            print("Token not valid")
            return Response(status=404)

        token = get_token(request)
        # collections = generate_collections_list(token.user)
        return Response(data={}, status=200)


class GetNamedCollectionView(RatelimitMixin, APIView):
    """Given a collection, return the associated metadata.
       We don't care about the username, but Singularity push requires it.
       GET /v1/collections/<username>/<name>
    """

    renderer_classes = (JSONRenderer,)
    ratelimit_key = "ip"
    ratelimit_rate = settings.VIEW_RATE_LIMIT
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = "GET"
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


class GetNamedContainerView(RatelimitMixin, APIView):
    """Given a collection and container name, return the associated metadata.
       GET /v1/containers/vsoch/dinosaur-collection/container
    """

    renderer_classes = (JSONRenderer,)
    ratelimit_key = "ip"
    ratelimit_rate = settings.VIEW_RATE_LIMIT
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = "GET"
    renderer_classes = (JSONRenderer,)

    def get(self, request, username, name, container):

        print("GET GetNamedContainerView")

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

        # Even if the container doesn't exist, we return response that it does,
        # And it's created in the next view.

        data = generate_collection_details(collection, containers, token.user)
        return Response(data={"data": data}, status=200)


class BuildContainersView(RatelimitMixin, APIView):
    """Return a simple list of containers
       POST /v1/build
       GET /v1/build/
       PUT /v1/build/.+/_cancel
    """
    renderer_classes = (JSONRenderer,)
    ratelimit_key = 'ip'
    ratelimit_rate = settings.VIEW_RATE_LIMIT
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = ('GET', 'POST',)
    renderer_classes = (JSONRenderer,)

    def post(self, request, format=None):

        print("POST BuildContainersView")
        raw=request.data.get('definitionRaw').encode()
        print(request.query_params)

        if not validate_token(request):
            print("Token not valid")
            return Response(status=404)
        token = get_token(request)
        user = token.user
        key = ''.join([random.choice(string.ascii_lowercase
                    + string.digits) for n in range(24)])
        filename = "/tmp/.{}.spec".format(key).encode()
        ret = lib.Unmarshal(GoString(raw,len(raw)),GoString(filename,len(filename)))
        data = {"id": key,"libraryRef": "{0}/remote-builds/rb-{1}".format(user,key)}
        return Response(data={"data": data}, status=200)

    def push_get(self, request, username, collection, name, version):

        print("BUILD PushNamedContainer")

        token = get_token(request)

        # Look up the collection
        try:
            collection = Collection.objects.get(name=collection)
        except Collection.DoesNotExist:
            return Response(status=404)

        if token.user not in collection.owners.all():
            return Response(status=403)

        # We have to generate a temporary tag, or it will overwrite latest
#        tag = "DUMMY-%s" % str(uuid.uuid4())
        tag = "latest"

        # The container will always be created, and it needs to be handled later
        container, created = Container.objects.get_or_create(
            collection=collection,
            name=name,
            frozen=False,
            tag=tag,
            version="sha256." + version,
        )

        arch = request.query_params.get('arch')
        if arch:
            container.metadata['arch'] = arch

        data = generate_container_metadata(container)
#        print("BUILD PUSH DATA: {}".format(data))
        return data

    def push_put(self, request, container_id, secret, filename, format=None):

        print("BUILD PUSH PUT: PushImageFileView")
        print(container_id)
        print(secret)

        # Look up the container
        try:
            container = Container.objects.get(id=container_id)
        except Container.DoesNotExist:
            return Response(status=404)

        # The secret must match the one just generated for the URL
        if container.metadata.get('pushSecret', 'nope') != secret:
            return Response(status=403)
        del container.metadata['pushSecret']

        # Create collection root, if it doesn't exist
        image_home = "%s/%s" %(settings.MEDIA_ROOT, container.collection.name)
        if not os.path.exists(image_home):
            os.mkdir(image_home)

        # Write the file to location
        from shub.apps.api.models import ImageFile
        container_path = os.path.join(image_home, "%s-%s.sif" % (container.name, container.version))
        shutil.move(filename, container_path)

#        file_obj = request.data['file']
#
#        with default_storage.open(container_path, 'wb+') as destination:
#            for chunk in file_obj.chunks():
#                destination.write(chunk)

        # Save newly uploaded file to model
        reopen = open(container_path, "rb")
        django_file = File(reopen)

        imagefile = ImageFile(collection=container.collection.name,
                              name=container_path)
        imagefile.datafile.save(container_path, django_file, save=True)
        container.image = imagefile
        container.save()

    def push_post(self, request, container_id):

        # Look up the container to set a temporary upload secret
        try:
            container = Container.objects.get(id=container_id)
        except Container.DoesNotExist:
            return Response(status=404)

        # check user permission
        token = get_token(request)
        if token.user not in container.collection.owners.all():
            return Response(status=403)

        push_secret = str(uuid.uuid4())
        container.metadata['pushSecret'] = push_secret
        container.save()

        # TODO this could check for Google Build, and return signed upload URL, or S3 signed URL
        url = settings.DOMAIN_NAME + reverse(
            "PushImageFileView", args=[str(container_id), push_secret]
        )

        data = {"uploadURL": url}
        return data

    def get(self, request, buildid, *args, **kwargs):

        print("GET BuildContainersView")
        print(request.data)
        print(request.query_params)
        if not validate_token(request):
            print("Token not valid")
            return Response(status=404)

        token = get_token(request)
        user = token.user

        libraryRef = "{0}/remote-builds/rb-{1}".format(user,buildid)
        libraryURL = settings.DOMAIN_NAME
#
        collection = "remote-builds"
        name = "rb-{}".format(buildid)
        data = self.push_get(request, user, collection, name, "latest")
        container_id = data['id']
#
#        return RequestPushImageFileView.as_view()(request, container_id, *args)
        data = self.push_post(request, container_id)
        secret = data['uploadURL'].split('/')[-1]
#
        filename = "/tmp/.{}.img".format(buildid)
        try:
            imageSize = os.path.getsize(filename)
        except FileNotFoundError:
            return Response(status=404)

        self.push_put(request, container_id, secret, filename)
#
# To be modify accordingly to real complete status
        isComplete = True
        data = {'imageSize': imageSize, 'isComplete': isComplete, 'libraryRef': libraryRef, 'libraryURL': libraryURL}
        print("data: {0}".format(data))
        return Response(data={"data": data}, status=200)
