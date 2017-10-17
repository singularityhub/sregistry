'''

Copyright (c) 2017, Vanessa Sochat, All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''

from django.conf.urls import url
from shub.settings import (
    DOMAIN_NAME,
    REGISTRY_URI,
    REGISTRY_NAME
)

from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.response import Response
import os
    


##############################################################################
# Registry Metadata
##############################################################################


class Registry(object):
    def __init__(self, **kwargs):
       self.name = REGISTRY_NAME
       self.id = REGISTRY_URI
       self.url = DOMAIN_NAME


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
    


#########################################################################
# urlpatterns
#########################################################################


urlpatterns = [

    url(r'^registry/identity/?$', RegistryViewSet.as_view({'get':'get'})),

]
