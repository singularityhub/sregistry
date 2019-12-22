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

from rest_framework.exceptions import ParseError
from rest_framework.parsers import FileUploadParser, MultiPartParser

from shub.apps.library.views.helpers import (
    generate_container_metadata,
    get_token,
    validate_token,
)

from shub.apps.library.views.images import (
    PushImageView,
    RequestPushImageFileView,
    PushImageFileView,
    CompletePushImageFileView,
)

import django_rq
import shutil
import tempfile
import json
import uuid
import os
import random
import string
import base64

class BuildContainersView(RatelimitMixin, APIView):
    """Build Containers
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
        raw=base64.b64decode(request.data.get('definitionRaw')).decode()
        print("definitionRaw: {}\n".format(raw))
        print(request.query_params)

        if not validate_token(request):
            print("Token not valid")
            return Response(status=404)
        token = get_token(request)
        user = token.user
        key = ''.join([random.choice(string.ascii_lowercase
                    + string.digits) for n in range(24)])
#        key = "zlrr25y81d5qy33mqnemr8wl"
        filename = "/tmp/.{}.spec".format(key).encode()
#        filename = "/tmp/.{}.spec".format(key)
        try:
            print("Writing spec file in {}...".format(filename))
            destname = open(filename, 'w')
            destname.write(raw)
            destname.close()
        except:
            print("Failed to write spec to file {}".format(filename))
            return Response(status=404)
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

    def get(self, request, buildid):

        print("GET BuildContainersView")
        print(request.data)
        print(request.query_params)
        if not validate_token(request):
            print("Token not valid")
            return Response(status=404)

        token = get_token(request)
        user = token.user

        tag = "latest"
        libraryRef = "{}/remote-builds/rb-{}:{}".format(user,buildid,tag)
        libraryURL = settings.DOMAIN_NAME
#
        collection = "remote-builds"
        name = "rb-{}".format(buildid)
        try:
            data = PushImageView.as_view()(request._request,
            username=user,
            collection=collection,
            name=name,
            version="latest"
            ).data['data']
#            data = self.push_get(request, user, collection, name, "latest")
            container_id = data['id']
            print("PushNamedContainerView data {}".format(data))
        except:
            print("Failed to GET PushNamedContainerView!")
            return Response(status=404)

#        try:
        request._request.method = 'POST'
        data = RequestPushImageFileView.as_view()(request._request,
        container_id=container_id
        ).data['data']
#         data = self.push_post(request, container_id)
        secret = data['uploadURL'].split('/')[-1]
        print("container_id {} secret: {}".format(container_id,secret))
#        except:
#            print("Failed to POST RequestPushImageFileView!")
#            return Response(status=404)

        filename = "/tmp/.{}.img".format(buildid)
        try:
            print("Retrieve file {} size...".format(filename))
            imageSize = os.path.getsize(filename)
        except FileNotFoundError:
            print("Failed to retrieve file {} size!".format(filename))
            return Response(status=404)

#        request._request.method = 'PUT'
##        data = FileUploadView.as_view()(request._request,
##        filename = filename
##        ).data
##        print(repr(request._request))
#        print(PushImageFileView.as_view()(request._request,
#        container_id=container_id,
#        secret=secret,
#        filename=filename
#        ).data)
#        self.push_put(request, container_id, secret, filename)
        try:
            request._request.method = 'PUT'
            data = PushImageFileView.as_view()(request._request,
            container_id=container_id,
            secret=secret,
            filename=filename
            )
        except:
            print("Failed to PUT PushImageFileView!")
            return Response(status=404)
#
        try:
            request._request.method = 'PUT'
            data = CompletePushImageFileView.as_view()(request._request,
            container_id=container_id
            )
        except:
            print("Failed to PUT CompletePushImageFileView!")
            return Response(status=404)

##
## To be modify accordingly to real complete status
        isComplete = True
        data = {'imageSize': imageSize, 'isComplete': isComplete, 'libraryRef': libraryRef, 'libraryURL': libraryURL}
        print("data: {0}".format(data))
        request._request.method = 'GET'
        return Response(data={"data": data}, status=200)
