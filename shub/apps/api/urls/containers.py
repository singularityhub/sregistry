"""

Copyright (C) 2017-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.conf import settings
from django.conf.urls import url
from django.urls import reverse

from shub.apps.api.utils import validate_request
from shub.apps.main.models import Container
from shub.apps.logs.mixins import LoggingMixin
from shub.apps.api.utils import has_permission

from sregistry.main.registry.auth import generate_timestamp

from rest_framework import generics, serializers, viewsets, status
from rest_framework.exceptions import PermissionDenied, NotFound
from ratelimit.mixins import RatelimitMixin
from rest_framework.response import Response
from rest_framework.views import APIView

################################################################################
# Single Object Serializers
################################################################################


class SingleContainerSerializer(serializers.ModelSerializer):

    collection = serializers.SerializerMethodField("collection_name")
    image = serializers.SerializerMethodField("get_download_url")
    metadata = serializers.SerializerMethodField("get_cleaned_metadata")

    def collection_name(self, container):
        return container.collection.name

    def get_cleaned_metadata(self, container):
        metadata = container.metadata
        for key in ["build_metadata", "builder", "build_finish", "image"]:
            if key in metadata:
                del metadata[key]
        return metadata

    def get_download_url(self, container):

        secret = container.collection.secret
        download_url = reverse(
            "download_container", kwargs={"cid": container.id, "secret": secret}
        )

        return "%s%s" % (settings.DOMAIN_NAME, download_url)

    class Meta:
        model = Container
        fields = (
            "id",
            "name",
            "image",
            "tag",
            "add_date",
            "metrics",
            "version",
            "tag",
            "frozen",
            "metadata",
            "collection",
        )


################################################################################
# Multiple Object Serializers
################################################################################


class ContainerSerializer(serializers.HyperlinkedModelSerializer):

    collection = serializers.SerializerMethodField("collection_name")
    metadata = serializers.SerializerMethodField("get_cleaned_metadata")

    def collection_name(self, container):
        return container.collection.name

    def get_cleaned_metadata(self, container):
        metadata = container.metadata
        for key in ["build_metadata", "builder", "build_finish", "image"]:
            if key in metadata:
                del metadata[key]
        return metadata

    class Meta:
        model = Container
        fields = (
            "id",
            "name",
            "tag",
            "add_date",
            "metrics",
            "version",
            "tag",
            "frozen",
            "metadata",
            "collection",
        )

    id = serializers.ReadOnlyField()


################################################################################
# ViewSets: requests for (paginated) information about containers
################################################################################


class ContainerViewSet(viewsets.ReadOnlyModelViewSet):
    """View all containers"""

    def get_queryset(self):
        return Container.objects.filter(collection__private=False)

    serializer_class = ContainerSerializer


################################################################################
# Container Views: custom views for specific containers
################################################################################


class ContainerDetailByName(LoggingMixin, RatelimitMixin, generics.GenericAPIView):
    """Retrieve a container instance based on it's name"""

    ratelimit_key = "ip"
    ratelimit_rate = settings.VIEW_RATE_LIMIT
    ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
    ratelimit_method = "GET"

    def get_object(
        self, collection, name, tag=None, version=None
    ):  # pylint: disable=arguments-differ

        try:

            # Given collection, container, tag and version
            if tag is not None and version is not None:
                container = Container.objects.get(
                    collection__name=collection, name=name, tag=tag, version=version
                )

            # Given collection, container, version
            elif tag is None:
                container = Container.objects.get(
                    collection__name=collection, name=name, version=version
                )
            # Given collection, container, tag
            elif version is None:
                container = Container.objects.get(
                    collection__name=collection, name=name, tag=tag
                )
            # Given collection, container
            else:
                container = Container.objects.get(
                    collection__name=collection, name=name
                )
        except Container.DoesNotExist:
            container = None
        return container

    def delete(self, request, collection, name, tag=None, version=None):
        from shub.apps.api.actions import delete_container
        from shub.apps.library.views.minio import delete_minio_container

        container = self.get_object(
            collection=collection, name=name, tag=tag, version=version
        )

        if container is None:
            full_name = "%s/%s" % (collection, name)
            container = self.get_object(collection=full_name, name=full_name, tag=tag)
        if container is None:
            raise NotFound(detail="Container Not Found")

        if container.frozen is True:
            message = "%s is frozen, delete not allowed." % container.get_short_uri()
            raise PermissionDenied(detail=message, code=304)

        # This only deletes container object, not remote builds.
        if delete_container(request, container):
            delete_minio_container(container)
            container.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        raise PermissionDenied(detail="Unauthorized")

    def get(self, request, collection, name, tag="latest", version=None):
        container = self.get_object(collection=collection, name=name, tag=tag)

        # if container None, likely is google build (container name includes collection)
        if container is None:
            full_name = "%s/%s" % (collection, name)
            container = self.get_object(collection=full_name, name=full_name, tag=tag)

        return _container_get(request, container, name, tag)


def _container_get(request, container, name=None, tag=None):
    """container get is the shared function for getting a container based
    on a name or an id. It validates the request and returns a response.

    Parameters
    ==========
    request: the request from the view with the user
    container: the container object to check
    """
    if container is None:
        raise NotFound

    if name is None:
        name = container.name

    if tag is None:
        tag = container.tag

    # The user isn't allowed to get more than the limit
    if container.get_count >= container.get_limit:
        return Response(429)

    if container.collection.get_count >= container.collection.get_limit:
        return Response(429)

    # All public images are pull-able

    is_private = container.collection.private

    if not is_private:
        serializer = SingleContainerSerializer(container)
        return Response(serializer.data)

    # Determine if user has permission to get if private
    auth = request.META.get("HTTP_AUTHORIZATION")

    if auth is None:
        print("Auth is None")
        raise PermissionDenied(detail="Authentication Required")

    # Validate User Permissions - must have view to pull private image

    if not has_permission(auth, container.collection):
        print("Does not have permission")
        raise PermissionDenied(detail="Unauthorized")

    timestamp = generate_timestamp()
    payload = "pull|%s|%s|%s|%s|" % (container.collection.name, timestamp, name, tag)

    if validate_request(auth, payload, "pull", timestamp):
        serializer = SingleContainerSerializer(container)
        return Response(serializer.data)

    return Response(400)


################################################################################
# Search
################################################################################


class ContainerSearch(APIView):
    """search for a list of containers depending on a query"""

    def get_object(self, name, collection, tag):
        from shub.apps.main.query import specific_container_query

        return specific_container_query(name=name, collection=collection, tag=tag)

    def get(self, request, name, collection=None, tag=None):
        containers = self.get_object(name, collection, tag)
        data = [ContainerSerializer(c).data for c in containers]
        return Response(data)


################################################################################
# urlpatterns
################################################################################

urlpatterns = [
    url(
        r"^container/search/collection/(?P<collection>.+?)/name/(?P<name>.+?)/tag/(?P<tag>.+?)/?$",
        ContainerSearch.as_view(),
    ),
    url(
        r"^container/search/collection/(?P<collection>.+?)/name/(?P<name>.+?)/?$",
        ContainerSearch.as_view(),
    ),
    url(
        r"^container/search/name/(?P<name>.+?)/tag/(?P<tag>.+?)/?$",
        ContainerSearch.as_view(),
    ),
    url(r"^container/search/name/(?P<name>.+?)/?$", ContainerSearch.as_view()),
    url(
        r"^container/(?P<collection>.+?)/(?P<name>.+?):(?P<tag>.+?)@(?P<version>.+?)/?$",
        ContainerDetailByName.as_view(),
    ),
    url(
        r"^container/(?P<collection>.+?)/(?P<name>.+?)@(?P<version>.+?)/?$",
        ContainerDetailByName.as_view(),
    ),
    url(
        r"^container/(?P<collection>.+?)/(?P<name>.+?):(?P<tag>.+?)/?$",
        ContainerDetailByName.as_view(),
    ),
    url(
        r"^container/(?P<collection>.+?)/(?P<name>.+?)/?$",
        ContainerDetailByName.as_view(),
    ),
]
