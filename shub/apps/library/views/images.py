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
from shub.settings import (
    MINIO_BUCKET,
    MINIO_EXTERNAL_SERVER,
    MINIO_SIGNED_URL_EXPIRE_MINUTES,
    MINIO_MULTIPART_UPLOAD,
)

from ratelimit.mixins import RatelimitMixin

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer

from .parsers import OctetStreamParser, EmptyParser
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .minio import minioClient, minioExternalClient, s3, s3_external
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

from datetime import timedelta
import django_rq
import shutil
import tempfile
import json
import uuid
import os
import re

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
        """In a post, the upload_id will be the container id.
        """
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


class RequestMultiPartPushImageFileView(RatelimitMixin, APIView):
    """Currently this view returns 404 to default to v2 RequestPushImageFileView
       see https://github.com/singularityhub/sregistry/issues/282
    """

    ratelimit_key = "ip"
    ratelimit_rate = settings.VIEW_RATE_LIMIT
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = "POST"
    renderer_classes = (JSONRenderer,)
    allowed_methods = (
        "POST",
        "PUT",
    )
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def put(self, request, upload_id):
        """In a put, we've started the multipart upload and are continuing the
           process.

           request.body includes:
              partSize: int64
              uploadID: string
              partNumber: int
              sha256sum: string
        """
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

        # Validate the uploadID
        if body.get("uploadID") != container.metadata.get("upload_id"):
            return Response(status=404)

        # The part number gets the presigned url
        part_number = str(body.get("partNumber"))

        # Return the next part
        presigned_url = container.metadata["upload_presigned_urls"].get(part_number)
        print(presigned_url)

        # Return the presigned url
        data = {"presignedURL": presigned_url}
        return Response(data={"data": data}, status=200)

    def post(self, request, upload_id):
        """In a post, the upload_id will be the container id.
        """

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

        # Filesize in bytes to calculate how to upload by
        filesize = body.get("filesize")
        max_size = 5 * 1024 * 1024
        upload_by = int(filesize / max_size) + 1

        # Key is the path in storage
        storage = container.get_storage()

        # Create the multipart upload
        res = s3.create_multipart_upload(Bucket=MINIO_BUCKET, Key=storage, HostID=MINIO_EXTERNAL_SERVER)
        print(res)
        # {'Bucket': 'sregistry',
        #  'Key': 'test/big:sha256.92278b7c046c0acf0952b3e1663b8abb819c260e8a96705bad90833d87ca0874',
        #  'ResponseMetadata': {'HTTPHeaders': {'accept-ranges': 'bytes',
        #    'content-length': '252',
        #    'content-security-policy': 'block-all-mixed-content',
        #    'content-type': 'application/xml',
        #    'date': 'Sat, 04 Apr 2020 19:59:30 GMT',
        #    'server': 'MinIO/RELEASE.2020-04-02T21-34-49Z',
        #    'vary': 'Origin',
        #    'x-amz-request-id': '1602B6380F9F9146',
        #    'x-xss-protection': '1; mode=block'},
        #   'HTTPStatusCode': 200,
        #   'HostId': '',
        #   'RequestId': '1602B6380F9F9146',
        #   'RetryAttempts': 0},
        #  'UploadId': '69399c6e-35b3-4b98-b000-164f0e5367a0'}

        upload_id = res["UploadId"]
        print("Start multipart upload %s" % upload_id)

        # Generate pre-signed URLS for external client (lookup by part number)
        urls = {}
        for part_number in range(1, upload_by + 1):
            signed_url = s3_external.generate_presigned_url(
                ClientMethod="upload_part",
                Params={
                    "Bucket": MINIO_BUCKET,
                    "Key": storage,
                    "UploadId": upload_id,
                    "PartNumber": part_number,
                },
                ExpiresIn=MINIO_SIGNED_URL_EXPIRE_MINUTES,
            )
            urls[part_number] = signed_url

        # s3_dest_client.upload_part(
        #                        Body=chunkdata,
        #                        Bucket=DesBucket,
        #                        Key=prefix_and_key,
        #                        PartNumber=partnumber,
        #                        UploadId=uploadId,
        #                        ContentMD5=base64.b64encode(chunkdata_md5.digest()).decode('utf-8')
        #                    )

        #      <input type="hidden" name="key" value="VALUE" />
        #      <input type="hidden" name="AWSAccessKeyId" value="VALUE" />
        #      <input type="hidden" name="policy" value="VALUE" />
        #      <input type="hidden" name="signature" value="VALUE" />

        # default_client_config = self.get_default_client_config()

        #    parts = []
        #    with target_file.open('rb') as fin:
        #        for num, url in enumerate(urls):
        #            part = num + 1
        #            file_data = fin.read(max_size)
        #            print(f"upload part {part} size={len(file_data)}")
        #            res = requests.put(url, data=file_data)
        #            print(res)
        #            if res.status_code != 200:
        #                return
        #            etag = res.headers['ETag']
        #            parts.append({'ETag': etag, 'PartNumber': part})

        #    print(parts)
        #    s3util.complete(parts)

        print(request)
        print(request.query_params)
        print(request.META)
        print(request.body)

        # Save parameters with container
        container.metadata["upload_id"] = upload_id
        container.metadata["upload_presigned_urls"] = urls
        container.metadata["upload_filesize"] = filesize
        container.metadata["upload_max_size"] = max_size
        container.metadata["upload_by"] = upload_by
        container.save()

        # Start a multipart upload
        data = {
            "uploadID": upload_id,
            "totalParts": len(urls),
            "partSize": upload_by,
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
            return Response(status=403)

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
