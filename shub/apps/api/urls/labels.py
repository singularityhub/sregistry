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
from django.http import Http404

import os

from shub.apps.api.urls.serializers import (
    HyperlinkedImageURL,
    SerializedContributors,
    HyperlinkedDownloadURL,
    HyperlinkedRelatedURL
)
from shub.apps.main.models import (
    Container, 
    Collection,
    Label
)


from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.response import Response
from rest_framework.views import APIView


##############################################################################
# Single Object Serializers
##############################################################################

class LabelSerializer(serializers.ModelSerializer):
    #containers = serializers.PrimaryKeyRelatedField(many=True, 
    #                                                queryset=Container.objects.all())

    containers = serializers.SerializerMethodField('list_containers')

    def list_containers(self, label):
        container_list = []
        for container in label.containers.all():
            container_list.append(container.get_uri())
        return container_list

    class Meta:
        model = Label
        fields = ('key','value','containers',)



#########################################################################
# ViewSets: requests for (paginated) information about containers
#########################################################################


class LabelViewSet(viewsets.ReadOnlyModelViewSet):
    '''View all labels
    '''

    def get_queryset(self):
        return Label.objects.filter(container__collection__private=False)
    serializer_class = LabelSerializer


#########################################################################
# Label Details: custom views for specific containers
#########################################################################

class LabelDetail(APIView):
    '''Retrieve a container instance based on it's name
    '''

    def get_object(self, key, value):
        # If not specified, return all
        if key is None and value is None:
            return Label.objects.all()

        if key is not None and value is not None:
            return Label.objects.filter(key=key,value=value)

        if key is None:
            return Label.objects.filter(value=value)

        return Label.objects.filter(key=key)

    def get(self, request, key=None, value=None):
        labels = self.get_object(key,value)
        data = [LabelSerializer(l).data for l in labels]
        return Response(data)
   

#########################################################################
# urlpatterns
#########################################################################

urlpatterns = [

    url(r'^labels/search$', LabelDetail.as_view()),                                        # all labels
    url(r'^labels/search/(?P<key>.+?)/key/(?P<value>.+?)/value$', LabelDetail.as_view()),  # key and value
    url(r'^labels/search/(?P<key>.+?)/key$', LabelDetail.as_view()),                       # key
    url(r'^labels/search/(?P<value>.+?)/value$', LabelDetail.as_view())   # value

]
