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
from rest_framework.exceptions import (
    PermissionDenied,
    NotFound
)

from shub.apps.api.utils import validate_request
from sregistry.auth import generate_timestamp

from django.urls import reverse
from django.http import Http404

import os
from shub.apps.main.models import Container, Collection

from rest_framework import generics
from shub.apps.logs.mixins import LoggingMixin
from shub.apps.main.query import container_lookup
from shub.apps.api.utils import has_permission

from rest_framework import serializers
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from shub.settings import (
    MEDIA_URL,
    DOMAIN_NAME
)


##############################################################################
# Single Object Serializers
##############################################################################

class SingleContainerSerializer(serializers.ModelSerializer):

    collection = serializers.SerializerMethodField('collection_name')
    image = serializers.SerializerMethodField('get_download_url')

    def collection_name(self, container):
        return container.collection.name

    def get_download_url(self, container):
        url = reverse('download_container', kwargs= {'cid':container.id,
                                                     'secret':container.secret})
        return "%s%s" %(DOMAIN_NAME,url)

    class Meta:
        model = Container
        fields = ('id','name','image','tag','add_date', 'metrics',
                  'version','tag','frozen', 'metadata', 'collection')


##############################################################################
# Multiple Object Serializers
##############################################################################


class ContainerSerializer(serializers.HyperlinkedModelSerializer):

    collection = serializers.SerializerMethodField('collection_name')

    def collection_name(self, container):
        return container.collection.name

    class Meta:
        model = Container
        fields = ('id','name','tag','add_date', 'metrics',
                  'version','tag', 'frozen', 'metadata', 'collection')

    id = serializers.ReadOnlyField()



#########################################################################
# ViewSets: requests for (paginated) information about containers
#########################################################################


class ContainerViewSet(viewsets.ReadOnlyModelViewSet):
    '''View all containers
    '''

    def get_queryset(self):
        return Container.objects.filter(collection__private=False)
        
    serializer_class = ContainerSerializer


#########################################################################
# Container Views: custom views for specific containers
#########################################################################


class ContainerDetailByName(LoggingMixin, generics.GenericAPIView):
    '''Retrieve a container instance based on it's name
    '''
    def get_object(self, collection, name, tag):

        try:
            if tag is not None:
                container = Container.objects.get(collection__name=collection,
                                                  name=name,
                                                  tag=tag)
            else:
                container = Container.objects.get(collection__name=collection,
                                                  name=name)
        except Container.DoesNotExist:
            container = None
        return container


    def delete(self, request, collection, name, tag=None):
        from shub.apps.api.actions import delete_container
        container = self.get_object(collection=collection, 
                                    name=name,
                                    tag=tag)

        if container is None:
            raise NotFound(detail="Container Not Found")

        if container.frozen is True:
            message = "%s is frozen, delete not allowed." %container.get_short_uri()
            raise PermissionDenied(detail=message, code=304)

        if delete_container(request,container) is True:
            container.delete()       
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise PermissionDenied(detail="Unauthorized")


    def get(self, request, collection, name, tag=None):
        container = self.get_object(collection=collection, 
                                    name=name,tag=tag)
        return _container_get(request, container, name, tag)


def _container_get(request, container, name=None, tag=None):
    '''container get is the shared function for getting a container based
       on a name or an id. It validates the request and returns a response.
       
       Parameters
       ==========
       request: the request from the view with the user
       container: the container object to check
    '''
    if container is None:
        return Response({})

    if name is None:
        name = container.name

    if tag is None:
        tag = container.tag

    serializer = SingleContainerSerializer(container)
    is_private = container.collection.private

    # All public images are pull-able

    if not is_private:
        return Response(serializer.data)

    # Determine if user has permission to get if private
    auth = request.META.get('HTTP_AUTHORIZATION')

    if auth is None:
        raise PermissionDenied(detail="Authentication Required")

    # Validate User Permissions - must have view to pull private image

    if not has_permission(auth, container.collection):
        raise PermissionDenied(detail="Unauthorized")

    timestamp = generate_timestamp()
    payload = "pull|%s|%s|%s|%s|" %(container.collection,
                                    timestamp,
                                    name,
                                    tag)

    if validate_request(auth, payload, "pull", timestamp):
        return Response(serializer.data)    


    return Response(400)


class ContainerDetailById(LoggingMixin, generics.GenericAPIView):
    '''Retrieve a container instance based on it's id
    '''
    def get_object(self, cid):
        from shub.apps.main.views.containers import get_container
        container = get_container(cid)
        return container

    def delete(self, request, cid):
        from shub.apps.api.actions import delete_container
        container = self.get_object(cid)
        if delete_container(request,container) is True:
            container.delete()       
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(400)
        
    def get(self, request, cid):
        container = self.get_object(cid)
        return _container_get(request, container)


#########################################################################
# Search
#########################################################################


class ContainerSearch(APIView):
    '''search for a list of containers depending on a query
    '''
    def get_object(self, name, collection, tag):
        from shub.apps.main.query import specific_container_query
        return specific_container_query(name=name,
                                        collection=collection,
                                        tag=tag)
        
    def get(self, request, name, collection=None, tag=None):
        containers = self.get_object(name,collection,tag)
        data = [ContainerSerializer(c).data for c in containers]
        return Response(data)
    

#########################################################################
# urlpatterns
#########################################################################

urlpatterns = [

    url(r'^container/search/collection/(?P<collection>.+?)/name/(?P<name>.+?)/tag/(?P<tag>.+?)/?$', ContainerSearch.as_view()),
    url(r'^container/search/collection/(?P<collection>.+?)/name/(?P<name>.+?)/?$', ContainerSearch.as_view()),
    url(r'^container/search/name/(?P<name>.+?)/tag/(?P<tag>.+?)/?$', ContainerSearch.as_view()),
    url(r'^container/search/name/(?P<name>.+?)/?$', ContainerSearch.as_view()),
    url(r'^container/(?P<collection>.+?)/(?P<name>.+?):(?P<tag>.+?)/?$', ContainerDetailByName.as_view()),
    url(r'^container/(?P<collection>.+?)/(?P<name>.+?)/?$', ContainerDetailByName.as_view()),
    url(r'^containers/(?P<cid>.+?)/?$', ContainerDetailById.as_view())

]
