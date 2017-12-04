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
from rest_framework.exceptions import (
    PermissionDenied,
    NotFound
)
from django.urls import reverse
from django.http import Http404

import os
from shub.apps.main.models import Container, Collection

from rest_framework import generics
from shub.apps.logs.mixins import LoggingMixin
from shub.apps.main.query import container_lookup

from rest_framework import serializers
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings

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
        return "%s%s" %(settings.DOMAIN_NAME,url)

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

        print(container)
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
        if container is None:
            return Response({})

        serializer = SingleContainerSerializer(container)
        is_private = container.collection.private
        if not is_private: 
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
        if container is None:
            return Response({})

        serializer = SingleContainerSerializer(container)
        is_private = container.collection.private
        if not is_private: 
            return Response(serializer.data)
    
        return Response(400)


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
