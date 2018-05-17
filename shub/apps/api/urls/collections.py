'''

Copyright (C) 2017-2018 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017-2018 Vanessa Sochat.

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

from shub.apps.api.urls.containers import ContainerSerializer
from shub.apps.api.utils import ObjectOnlyPermissions
from shub.apps.main.models import Container, Collection

from shub.apps.main.query import (
    container_lookup,
    collection_query,
    container_query
)

from django.conf import settings

from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.response import Response
from rest_framework.views import APIView
    

##############################################################################
# Single Object Serializers
##############################################################################

class CollectionSerializer(serializers.HyperlinkedModelSerializer):

    containers = serializers.SerializerMethodField('list_containers')

    def list_containers(self, collection):
        container_list = []
        for c in collection.containers.all():
            entry = {"name": c.name,
                     "tag": c.tag,
                     "uri": c.get_uri(),
                     "detail": "%s/containers/%s" %(settings.DOMAIN_NAME, c.id)}
            container_list.append(entry)
        return container_list

    class Meta:
        model = Collection
        fields = ('id','name','add_date','modify_date',
                  'metadata', 'containers')



#########################################################################
# ViewSets
# requests for (paginated) information about containers and collections
#########################################################################



class CollectionViewSet(viewsets.ReadOnlyModelViewSet):
    '''View all collections
    '''
    queryset = Collection.objects.filter(private=False)
    serializer_class = CollectionSerializer
    permission_classes = (ObjectOnlyPermissions,)



#########################################################################
# Container Details: custom views for specific collections
#########################################################################


class CollectionDetailByName(APIView):
    """Retrieve a collection instance based on it's name
    """
    def get_object(self, collection_name):
        try:
            collection = Collection.objects.get(name=collection_name.lower())
        except Collection.DoesNotExist:
            collection = None
        return collection

    def get(self, request, collection_name):
        collection = self.get_object(collection_name)

        if collection is None:
            return Response({})

        if collection.private is False:
            serializer = CollectionSerializer(collection)
            return Response(serializer.data)
    


#########################################################################
# Search
#########################################################################


class CollectionSearch(APIView):
    """search for a list of collections depending on a query. This is
    a general search to look across all fields for one term
    """
    def get_object(self, query):
        from shub.apps.main.query import collection_query
        collections = collection_query(query.lower())
        return collections

    def get(self, request, query):
        collections = self.get_object(query)
        serializer = CollectionSerializer(collections)
        return Response(serializer.data)    


#########################################################################
# urlpatterns
#########################################################################


urlpatterns = [

    url(r'^collection/search/(?P<query>.+?)/?$', CollectionSearch.as_view()),
    url(r'^collection/(?P<collection_name>.+?)/?$', CollectionDetailByName.as_view()),

]
