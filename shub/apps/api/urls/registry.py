"""

Copyright (C) 2017-2021 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.conf.urls import url
from django.conf import settings
from rest_framework import serializers, viewsets
from rest_framework.response import Response


################################################################################
# Registry Metadata
################################################################################


class Registry(object):
    def __init__(self, **kwargs):
        self.name = settings.REGISTRY_NAME
        self.id = settings.REGISTRY_URI
        self.url = settings.DOMAIN_NAME


class RegistrySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256)
    id = serializers.CharField(max_length=256)
    url = serializers.CharField(max_length=256)

    def list(self):
        return Registry()


class RegistryViewSet(viewsets.ViewSet):
    serializer_class = RegistrySerializer

    def get_object(self):
        return Registry()

    def get(self, request):
        registry = self.get_object()
        serializer = RegistrySerializer(registry)
        return Response(serializer.data)


################################################################################
# urlpatterns
################################################################################


urlpatterns = [url(r"^registry/identity/?$", RegistryViewSet.as_view({"get": "get"}))]
