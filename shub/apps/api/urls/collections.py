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

from shub.apps.api.urls.containers import ContainerSerializer
from shub.apps.api.utils import ObjectOnlyPermissions
from shub.apps.main.models import Container, Collection

from shub.apps.main.query import container_lookup
from shub.settings import DOMAIN_NAME

from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.response import Response
from rest_framework.views import APIView
    

##############################################################################
# Single Object Serializers
##############################################################################

class CollectionSerializer(serializers.ModelSerializer):
    '''A single collection is a set of containers of the same reponame/containername
    '''

    containers = serializers.SerializerMethodField('list_containers')

    def list_containers(self, collection):
        container_list = []
        for c in collection.containers.all():
            container_list.append("%s/containers/%s" %(DOMAIN_NAME, c.id))
        return container_list

    class Meta:
        model = Collection
        fields = ('name','add_date','modify_date',
                  'metadata', 'containers')



##############################################################################
# Multiple Object Serializers
##############################################################################

class CollectionSerializer(serializers.HyperlinkedModelSerializer):

    containers = serializers.SerializerMethodField('list_containers')

    def list_containers(self, collection):
        container_list = []
        for c in collection.containers.all():
            container_list.append("%s/containers/%s" %(DOMAIN_NAME, c.id))
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
            raise Http404
        return collection

    def get(self, request, collection_name):
        collection = self.get_object(collection_name)

        if not collection.private:
            serializer = CollectionSerializer(collection)
            return Response(serializer.data)
    
        return Response(400)



#########################################################################
# urlpatterns
#########################################################################


urlpatterns = [

    url(r'^collection/(?P<collection_name>.+?)$', CollectionDetailByName.as_view())

]
