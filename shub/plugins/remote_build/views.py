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
import requests

class BuildContainersView(RatelimitMixin, APIView):
    """Build Containers
       POST /v1/build
       GET /v1/build/
       PUT /v1/build/.+/_cancel
    """
    ratelimit_key = 'ip'
    ratelimit_rate = settings.VIEW_RATE_LIMIT
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = ('GET', 'POST',)
    renderer_classes = (JSONRenderer,)

    def post(self, request, format=None):

        print("POST BuildContainersView")
        raw=base64.b64decode(request.data.get('definitionRaw')).decode()
        print(request.query_params)

        if not validate_token(request):
            print("Token not valid")
            return Response(status=404)

        token = get_token(request)
        user = token.user
        # Define randomly container image name...
        key = ''.join([random.choice(string.ascii_lowercase
                    + string.digits) for n in range(24)])
        filename = "/tmp/.{}.spec".format(key).encode()
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

class PushContainersView(RatelimitMixin, APIView):
    """Push Container image
       POST /v1/push
       GET /v1/push/<buildid>
    """
    ratelimit_key = 'ip'
    ratelimit_rate = settings.VIEW_RATE_LIMIT
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = ('GET', 'POST',)
    renderer_classes = (JSONRenderer,)

    def get(self, request, buildid):

        print("GET PushContainersView")
        print(request.query_params)
        if not validate_token(request):
            print("Token not valid")
            return Response(status=404)

        token = get_token(request)
        user = token.user

        tag = "latest"
        collection = "remote-builds"
        name = "rb-{}".format(buildid)
        libraryURL = settings.DOMAIN_NAME
        filename = "/tmp/.{}.img".format(buildid)

        from sregistry.utils import get_file_hash
        version = get_file_hash(filename, "sha256")
        libraryRef = "{}/remote-builds/rb-{}:sha256.{}".format(user,buildid,version)

        try:
            print("Retrieve file {} size...".format(filename))
            imageSize = os.path.getsize(filename)
        except FileNotFoundError:
            print("Failed to retrieve file {} size!".format(filename))
            return Response(status=404)

#
        try:
            data = PushImageView.as_view()(request._request,
            username=user,
            collection=collection,
            name=name,
            version=version
            ).data['data']
            container_id = data['id']
            print("PushNamedContainerView data {}".format(data))
        except:
            print("Failed to GET PushNamedContainerView!")
            return Response(status=404)

        try:
            request._request.method = 'POST'
            data = RequestPushImageFileView.as_view()(request._request,
            container_id=container_id
            ).data['data']
            url = data['uploadURL']
            secret = url.split('/')[-1]
        except:
            print("Failed to POST RequestPushImageFileView!")
            return Response(status=404)

        data = open(filename, 'rb')
        headers = {'Content-type': 'application/octet-stream','Authorization': request.META.get("HTTP_AUTHORIZATION")}
        r = requests.put(url, data=data, headers=headers)
#
        try:
            request._request.method = 'PUT'
            data = CompletePushImageFileView.as_view()(request._request,
            container_id=container_id
            )
        except:
            print("Failed to PUT CompletePushImageFileView!")
            return Response(status=404)

## To be modify accordingly to real complete status
        isComplete = True
        data = {'imageSize': imageSize, 'isComplete': isComplete, 'libraryRef': libraryRef, 'libraryURL': libraryURL}
        request._request.method = 'GET'
        return Response(data={"data": data}, status=200)
