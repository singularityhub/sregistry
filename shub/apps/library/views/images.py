"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.conf import settings
from django.shortcuts import redirect, reverse
from sregistry.utils import parse_image_name

from shub.apps.logs.utils import generate_log
from shub.apps.main.utils import format_collection_name
from shub.apps.main.models import Collection, Container
from shub.settings import (
    MINIO_BUCKET,
    MINIO_REGION,
    MINIO_SIGNED_URL_EXPIRE_MINUTES,
    MINIO_MULTIPART_UPLOAD,
)

from ratelimit.mixins import RatelimitMixin

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer

from .parsers import EmptyParser
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .minio import (
    delete_minio_container,
    minioExternalClient,
    s3,
    s3_external,
    sregistry_presign_v4,
)
from .helpers import (
    generate_collection_tags,
    generate_collections_list,
    generate_collection_details,  # includes containers
    generate_collection_metadata,
    generate_container_metadata,
    get_token,
    get_container,
    get_collection,
    validate_token,
)

from urllib.parse import urlparse
from datetime import timedelta
import django_rq
import json
import uuid

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


class RequestMultiPartAbortView(RatelimitMixin, APIView):
    """Currently this view returns 404 to default to v2 RequestPushImageFileView
    see https://github.com/singularityhub/sregistry/issues/282
    """

    ratelimit_key = "ip"
    ratelimit_rate = settings.VIEW_RATE_LIMIT
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = "PUT"
    renderer_classes = (JSONRenderer,)
    allowed_methods = ("PUT",)

    def put(self, request, upload_id):
        """In a post, the upload_id will be the container id."""
        print("PUT RequestMultiPartAbortView")

        # Handle authorization
        if not validate_token(request):
            print("Token not valid")
            return Response(status=403)

        # Look up the container to set a temporary upload secret
        try:
            container = Container.objects.get(id=upload_id)
        except Container.DoesNotExist:
            return Response(status=404)

        container.delete()
        return Response(status=200)


class RequestMultiPartCompleteView(RatelimitMixin, APIView):
    """Complete the multipart upload."""

    ratelimit_key = "ip"
    ratelimit_rate = settings.VIEW_RATE_LIMIT
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = "PUT"
    renderer_classes = (JSONRenderer,)
    allowed_methods = ("PUT",)

    def put(self, request, upload_id):
        """A put is done to complete the upload, providing the image id and number parts
        https://github.com/sylabs/scs-library-client/blob/30f9b6086f9764e0132935bcdb363cc872ac639d/client/push.go#L537
        """
        print("PUT RequestMultiPartCompleteView")

        # Handle authorization
        if not validate_token(request):
            print("Token not valid")
            return Response(status=403)

        # body has {'uploadID': 'xxx', 'completedParts': []} each completed part has a token which is the Etag
        # {"partNumber":2,"token":'"684929e7fe8b996d495e7b152d34ae37-1"'}
        body = json.loads(request.body.decode("utf-8"))

        # Assemble list of parts as they are expected for Python client
        parts = [
            {"ETag": x["token"].strip('"'), "PartNumber": x["partNumber"]}
            for x in body["completedParts"]
        ]

        try:
            container = Container.objects.get(id=upload_id)
        except Container.DoesNotExist:
            return Response(status=404)

        # Complete the multipart upload
        res = s3.complete_multipart_upload(
            Bucket=MINIO_BUCKET,
            Key=container.get_storage(),
            MultipartUpload={"Parts": parts},
            UploadId=body.get("uploadID"),
            # RequestPayer='requester'
        )

        print(res)
        # Currently this response data is empty
        # https://github.com/sylabs/scs-library-client/blob/master/client/response.go#L97
        return Response(status=200, data={})


class RequestMultiPartPushImageFileView(APIView):
    """This POST view will returns 404 to default to v2 RequestPushImageFileView
    if MINIO_MULTIPART_UPLOAD is set to False. The PUT view handles generation
    of each multipart upload url.
    see https://github.com/singularityhub/sregistry/issues/282
    """

    renderer_classes = (JSONRenderer,)
    allowed_methods = (
        "POST",
        "PUT",
    )
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def put(self, request, upload_id):
        """After starting the multipart upload continue the process"""
        print("PUT RequestMultiPartPushImageFileView")

        # Check Authorization
        if not validate_token(request):
            print("Token not valid")
            return Response(status=403)

        # Get the container
        try:
            container = Container.objects.get(id=upload_id)
        except Container.DoesNotExist:
            return Response(status=404)

        # Get the request body
        body = json.loads(request.body.decode("utf-8"))
        upload_id = body.get("uploadID")
        storage = container.get_storage()
        sha256 = body.get("sha256sum")
        content_size = body.get("partSize")

        # partSize: int64
        # uploadID: string
        # partNumber: int
        # sha256sum: string

        # Validate the uploadID
        if upload_id != container.metadata.get("upload_id"):
            return Response(status=404)

        # The part number gets the presigned url
        part_number = int(body.get("partNumber"))

        # Generate pre-signed URLS for external client (lookup by part number)
        # We don't technically need this function, but it's preserved here in
        # case a future implementation can support providing a sha256sum to be included
        signed_url = s3_external.generate_presigned_url(
            ClientMethod="upload_part",
            HttpMethod="PUT",
            Params={
                "Bucket": MINIO_BUCKET,
                "Key": storage,
                "UploadId": upload_id,
                "PartNumber": part_number,
                "ContentLength": content_size,
            },
            ExpiresIn=timedelta(minutes=MINIO_SIGNED_URL_EXPIRE_MINUTES).seconds,
        )

        # Split the url to only include UploadID and PartNumber parameters
        parsed = urlparse(signed_url)
        params = {
            x.split("=")[0]: x.split("=")[1]
            for x in parsed.query.split("&")
            if not x.startswith("X-Amz")
        }
        new_url = parsed.scheme + "://" + parsed.netloc + parsed.path

        # Derive headers in the same way that Minio does, but include the sha256sum
        signed_url = sregistry_presign_v4(
            "PUT",
            new_url,
            region=MINIO_REGION,
            content_hash_hex=sha256,
            credentials=minioExternalClient._credentials,
            expires=str(timedelta(minutes=MINIO_SIGNED_URL_EXPIRE_MINUTES).seconds),
            headers={"X-Amz-Content-Sha256": sha256},
            response_headers=params,
        )

        # Return the presigned url
        data = {"presignedURL": signed_url}
        return Response(data={"data": data}, status=200)

    def post(self, request, upload_id):
        """In a post, the upload_id will be the container id."""

        print("POST RequestMultiPartPushImageFileView")

        # Handle authorization
        if not validate_token(request):
            print("Token not valid")
            return Response(status=403)

        # The admin can disable multipart uploads
        if not MINIO_MULTIPART_UPLOAD:
            return Response(status=404)

        # Look up the container to set a temporary upload secret
        try:
            container = Container.objects.get(id=upload_id)
        except Container.DoesNotExist:
            return Response(status=404)

        # The body provides a filesize
        body = json.loads(request.body.decode("utf-8"))
        if "filesize" not in body:
            return Response(status=400)

        # Filesize in bytes to calculate how to upload by (max size ~0.5 GB)
        filesize = body.get("filesize")
        max_size = 500 * 1024 * 1024
        upload_by = int(filesize / max_size) + 1

        # Key is the path in storage, MUST be encoded and quoted!
        storage = container.get_storage()

        # Create the multipart upload
        res = s3.create_multipart_upload(Bucket=MINIO_BUCKET, Key=storage)
        upload_id = res["UploadId"]
        print("Start multipart upload %s" % upload_id)

        # Calculate the total number of parts needed
        total_parts = len(range(1, upload_by + 1))

        # Save parameters with container
        container.metadata["upload_id"] = upload_id
        container.metadata["upload_filesize"] = filesize
        container.metadata["upload_max_size"] = max_size
        container.metadata["upload_by"] = upload_by
        container.metadata["upload_total_parts"] = total_parts
        container.save()

        # Start a multipart upload, telling Singularity how many parts and the size
        data = {
            "uploadID": upload_id,
            "totalParts": total_parts,
            "partSize": max_size,
        }
        return Response(data={"data": data}, status=200)


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
            return Response(status=403)

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

        # Get the container name and generate signed url
        storage = container.get_storage()
        url = minioExternalClient.presigned_put_object(
            MINIO_BUCKET,
            storage,
            expires=timedelta(minutes=MINIO_SIGNED_URL_EXPIRE_MINUTES),
        )

        # The external client is different from internal
        data = {"uploadURL": url}
        return Response(data={"data": data}, status=200)


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
            return Response(status=403)

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
    This view is used for manual download in the interface.
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

            # The user is not authenticated
            if not token:
                return Response(status=404)

            # Only owners and contributors can pull
            collection = container.collection
            if (
                token.user not in collection.owners.all()
                and token.user not in collection.contributors.all()
            ):
                return Response(status=404)

        # Retrieve the url for minio
        storage = container.get_storage()
        url = minioExternalClient.presigned_get_object(
            MINIO_BUCKET,
            storage,
            expires=timedelta(minutes=MINIO_SIGNED_URL_EXPIRE_MINUTES),
        )
        return redirect(url)


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

    ratelimit_key = "ip"
    ratelimit_rate = settings.VIEW_RATE_LIMIT
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = ("GET", "POST")
    renderer_classes = (JSONRenderer,)

    def get(self, request):
        """Return a simple list of collections.

        GET /v1/collections
        """

        print("GET CollectionsView")
        if not validate_token(request):
            print("Token not valid")
            return Response(status=403)

        token = get_token(request)
        collections = generate_collections_list(token.user)
        return Response(data=collections, status=200)

    def post(self, request):
        """Create a new collection.

        POST /v1/collections

        Body parameters:
        * entity: entity id (= user id)
        * name: new collection name
        * private: optional boolean (defaults to the configured default for
          new collections

        Return the newly created collection.
        """

        print("POST CollectionsView")
        if not validate_token(request):
            print("Token not valid")
            return Response(status=403)

        # body should have {'entity': entity_id, 'name': new_collection_name, 'private': bool}
        # 'private' is optional and defaults to Collection.private default
        # value set with get_privacy_default()
        # {"entity": "42", "name": "my_collection", "private": true}
        body = json.loads(request.body.decode("utf-8"))
        if not ("entity" in body and "name" in body):
            print("Invalid payload")
            return Response(status=400)

        # does a collection with the same name exist already?
        if not get_collection(body["name"], False) is None:
            print("A collection named '{0}' exists already!".format(body["name"]))
            return Response(status=403)

        # check user permission
        token = get_token(request)
        if str(token.user.id) != body["entity"]:
            print("Permission denied {0} {1}".format(token.user.id, body["entity"]))
            return Response(status=403)

        # create the collection
        name = format_collection_name(body["name"])
        collection = Collection(name=name, secret=str(uuid.uuid4()))
        collection.save()
        collection.owners.add(token.user)
        collection.save()

        # set privacy if present
        if "private" in body:
            collection.private = body["private"]
            collection.save()

        details = generate_collection_metadata(collection, token.user)
        return Response(data={"data": details}, status=200)


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
            return Response(status=403)

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
            return Response(status=403)

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
                container.delete()
                return Response(
                    {"message": "This tag exists, and is frozen."}, status=400
                )

            # Case 2: Exists and not frozen (replace)
            storage = existing.get_storage()
            if storage != container.get_storage():
                delete_minio_container(existing)

            # Now delete the container object
            existing.delete()
            selected = container

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
            return Response(status=403)

        # token = get_token(request)
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
            return Response(status=403)

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
            return Response(status=403)

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
