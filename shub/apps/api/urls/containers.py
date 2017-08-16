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
from django.urls import reverse
from django.http import Http404

import os
from shub.apps.api.utils import ObjectOnlyPermissions
from shub.apps.main.models import Container, Collection

from shub.apps.main.query import container_lookup

from rest_framework import serializers
from rest_framework import viewsets
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

    collection = serializers.PrimaryKeyRelatedField(queryset=Collection.objects.all())
    image = serializers.SerializerMethodField('get_download_url')

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

    class Meta:
        model = Container
        fields = ('id','name','tag','add_date', 'metrics',
                  'version','tag', 'frozen', 'metadata')

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


class ContainerDetailByName(APIView):
    """Retrieve a container instance based on it's name
    """
    def get_object(self, collection_name, container_name, container_tag):
        container = container_lookup(collection=collection_name, 
                                     name=container_name, 
                                     tag=container_tag)
        if container is not None:
            return container
        raise Http404

    def get(self, request, collection_name, container_name, container_tag=None):
        container = self.get_object(collection_name, container_name, container_tag)
        serializer = SingleContainerSerializer(container)
        is_private = container.collection.private
        if not is_private: 
            return Response(serializer.data)
    
        return Response(400)



class ContainerDetailById(APIView):
    """Retrieve a container instance based on it's id
    """
    def get_object(self, cid):
        from shub.apps.main.views.containers import get_container
        container = get_container(cid)
        if container is not None:
            return container
        raise Http404

    def get(self, request, cid):
        container = self.get_object(cid)
        serializer = SingleContainerSerializer(container)
        is_private = container.collection.private
        if not is_private: 
            return Response(serializer.data)
    
        return Response(400)


#########################################################################
# urlpatterns
#########################################################################

urlpatterns = [

    url(r'^container/(?P<collection_name>.+?)/(?P<container_name>.+?):(?P<container_tag>.+?)$', ContainerDetailByName.as_view()),
    url(r'^container/(?P<collection_name>.+?)/(?P<container_name>.+?)$', ContainerDetailByName.as_view()),
    url(r'^containers/(?P<cid>.+?)$', ContainerDetailById.as_view())

]
