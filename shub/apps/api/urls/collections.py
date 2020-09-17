"""

Copyright (C) 2017-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.conf.urls import url
from django.conf import settings

from shub.apps.api.utils import ObjectOnlyPermissions
from shub.apps.main.models import Collection
from shub.apps.main.query import collection_query

from rest_framework import serializers, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

################################################################################
# Single Object Serializers
################################################################################


class CollectionSerializer(serializers.HyperlinkedModelSerializer):

    containers = serializers.SerializerMethodField("list_containers")

    def list_containers(self, collection):
        container_list = []
        for c in collection.containers.all():
            entry = {
                "name": c.name,
                "tag": c.tag,
                "uri": c.get_uri(),
                "detail": "%s/containers/%s" % (settings.DOMAIN_NAME, c.id),
            }
            container_list.append(entry)
        return container_list

    class Meta:
        model = Collection
        fields = ("id", "name", "add_date", "modify_date", "metadata", "containers")


################################################################################
# ViewSets
# requests for (paginated) information about containers and collections
################################################################################


class CollectionViewSet(viewsets.ReadOnlyModelViewSet):
    """View all collections"""

    queryset = Collection.objects.filter(private=False)
    serializer_class = CollectionSerializer
    permission_classes = (ObjectOnlyPermissions,)


################################################################################
# Container Details: custom views for specific collections
################################################################################


class CollectionDetailByName(APIView):
    """Retrieve a collection instance based on it's name"""

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


################################################################################
# Search
################################################################################


class CollectionSearch(APIView):
    """search for a list of collections depending on a query. This is
    a general search to look across all fields for one term
    """

    def get_object(self, query):
        collections = collection_query(query.lower())
        return collections

    def get(self, request, query):
        collections = self.get_object(query)
        serializer = CollectionSerializer(collections)
        return Response(serializer.data)


################################################################################
# urlpatterns
################################################################################


urlpatterns = [
    url(r"^collection/search/(?P<query>.+?)/?$", CollectionSearch.as_view()),
    url(r"^collection/(?P<collection_name>.+?)/?$", CollectionDetailByName.as_view()),
]
