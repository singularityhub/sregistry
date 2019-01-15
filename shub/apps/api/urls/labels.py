'''

Copyright (C) 2017-2019 Vanessa Sochat.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

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


################################################################################
# Single Object Serializers
################################################################################

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



################################################################################
# ViewSets: requests for (paginated) information about containers
################################################################################

class LabelViewSet(viewsets.ReadOnlyModelViewSet):
    '''View all labels
    '''

    def get_queryset(self):
        return Label.objects.filter(container__collection__private=False)
    serializer_class = LabelSerializer


################################################################################
# Label Details: custom views for specific containers
################################################################################

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
   

################################################################################
# urlpatterns
################################################################################

urlpatterns = [

    url(r'^labels/search/?$', LabelDetail.as_view()),                                        # all labels
    url(r'^labels/search/(?P<key>.+?)/key/(?P<value>.+?)/value/?$', LabelDetail.as_view()),  # key and value
    url(r'^labels/search/(?P<key>.+?)/key/?$', LabelDetail.as_view()),                       # key
    url(r'^labels/search/(?P<value>.+?)/value/?$', LabelDetail.as_view())   # value

]
