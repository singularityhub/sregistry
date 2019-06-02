'''

Copyright (C) 2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser
from shub.apps.main.models import (
    Collection, 
    Container
)
from rest_framework.viewsets import ModelViewSet
from shub.apps.google_build.models import RecipeFile
from rest_framework import serializers
from sregistry.main.registry.auth import generate_timestamp

class RecipePushSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = RecipeFile
        read_only_fields = ('created', 'datafile','collection','tag','name',)
        fields = ('created', 'datafile','collection','tag','name')


class RecipePushViewSet(ModelViewSet):
    '''pushing a recipe coincides with doing a remote build.
    '''
    queryset = RecipeFile.objects.all()
    serializer_class = RecipePushSerializer
    parser_classes = (MultiPartParser, FormParser,)

    def perform_create(self, serializer):
 
        tag = self.request.data.get('tag','latest')                                   
        name = self.request.data.get('name')
        auth = self.request.META.get('HTTP_AUTHORIZATION', None)
        collection_name = self.request.data.get('collection')

        # Authentication always required for push

        if auth is None:
            raise PermissionDenied(detail="Authentication Required")

        owner = get_request_user(auth)
        timestamp = generate_timestamp()
        payload = "build|%s|%s|%s|%s|" %(collection_name,
                                         timestamp,
                                         name,
                                         tag)


        # Validate Payload

        if not validate_request(auth, payload, "build", timestamp):
            raise PermissionDenied(detail="Unauthorized")

        create_new = False

        # Determine the collection to build the recipe to
        try:
            collection = Collection.objects.get(name = collection_name)

            # Only owners can push
            if not owner in collection.owners.all():
                raise PermissionDenied(detail="Unauthorized")

        except Collection.DoesNotExist:
            collection = None
            create_new = True

        # Validate User Permissions

        if not has_permission(auth, collection, pull_permission=False):
            raise PermissionDenied(detail="Unauthorized")
        
        if collection is not None:

            # Determine if container is frozen
            try:
                container = Container.objects.get(collection=collection,
                                                  name=name,
                                                  tag=tag)
                if container.frozen is False:
                    create_new = True

            except Container.DoesNotExist:
                create_new=True
         


        # Create the recipe to trigger a build
 
        if create_new is True:
            serializer.save(datafile=self.request.data.get('datafile'),
                            collection=self.request.data.get('collection'),
                            tag=self.request.data.get('tag','latest'),
                            name=self.request.data.get('name'),
                            owner_id=owner.id)
        else:
            raise PermissionDenied(detail="%s is frozen, push not allowed." %container.get_short_uri())
