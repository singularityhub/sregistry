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

from rest_framework.parsers import FormParser, MultiPartParser
from shub.apps.main.models import Collection,Container
from rest_framework.viewsets import ModelViewSet
from shub.apps.api.models import ImageFile
from rest_framework import serializers
from shub.apps.api.utils import (
    JsonResponseMessage,
    validate_request
)

class ContainerPushSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ImageFile
        read_only_fields = ('created', 'datafile','collection','tag','name', 'metadata',)
        fields = ('created', 'datafile','collection','tag','name', 'metadata')


class ContainerPushViewSet(ModelViewSet):

    queryset = ImageFile.objects.all()
    serializer_class = ContainerPushSerializer
    parser_classes = (MultiPartParser, FormParser,)

    def perform_create(self, serializer):
 
        tag=self.request.data.get('tag','latest')                                   
        name=self.request.data.get('name')
        signature=self.requests.POST.get('HTTP_SREGISTRY_EVENT', None)
        if signature is None:
            return JsonResponseMessage(status=403, message="Authentication Required")


        if not signature_valid():

        create_new=False

        try:
            collection = Collection.objects.get(name=self.request.data.get('collection')) 
        except Collection.DoesNotExist:
            collection = None
            create_new=True
        
        if collection is not None:
            try:
                container = Container.objects.get(collection=collection,
                                                  tag=tag,
                                                  name=name)
                if container.frozen is False:
                    create_new = True
            except Container.DoesNotExist:
                create_new=True

        if create_new is True:
            serializer.save(datafile=self.request.data.get('datafile'),
                            collection=self.request.data.get('collection'),
                            tag=self.request.data.get('tag','latest'),
                            name=self.request.data.get('name'),
                            metadata=self.request.data.get('metadata'))
