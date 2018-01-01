'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017 Vanessa Sochat.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from shub.logger import bot
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser
from shub.apps.main.models import Collection,Container
from rest_framework.viewsets import ModelViewSet
from shub.apps.api.models import ImageFile
from rest_framework import serializers
from shub.apps.api.utils import validate_request
from singularity.registry.auth import generate_timestamp

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
        auth=self.request.META.get('HTTP_AUTHORIZATION', None)
        collection_name=self.request.data.get('collection')

        if auth is None:
            raise PermissionDenied(detail="Authentication Required")

        timestamp = generate_timestamp()
        payload = "push|%s|%s|%s|%s|" %(collection_name,
                                        timestamp,
                                        name,
                                        tag)

        if not validate_request(auth,payload,"push",timestamp):
            raise PermissionDenied(detail="Unauthorized")

        create_new=False

        try:
            collection = Collection.objects.get(name=collection_name) 
        except Collection.DoesNotExist:
            collection = None
            create_new=True
        
        if collection is not None:
            try:
                container = Container.objects.get(collection=collection,
                                                  name=name,
                                                  tag=tag)
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
        else:
            raise PermissionDenied(detail="%s is frozen, push not allowed." %container.get_short_uri())
