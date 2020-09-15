"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.shortcuts import render, redirect

from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser

from shub.apps.main.views import get_container, get_collection

from shub.apps.main.models import Collection, Container

from shub.apps.api.utils import get_request_user, validate_request, has_permission

from shub.settings import (
    DISABLE_GITHUB,
    DISABLE_BUILDING,
    DISABLE_BUILD_RECEIVE,
    SREGISTRY_GOOGLE_BUILD_LIMIT,
    VIEW_RATE_LIMIT as rl_rate,
    VIEW_RATE_LIMIT_BLOCK as rl_block,
)

from sregistry.main.registry.auth import generate_timestamp
from .github import (
    create_webhook,
    get_repo,
    list_repos,
    receive_github_hook,
    update_webhook_metadata,
)

from .models import RecipeFile
import django_rq
from datetime import timedelta

from .actions import (
    complete_build,
    delete_build,
    delete_container_collection,
    is_over_limit,
)

from .utils import JsonResponseMessage, validate_jwt

from ratelimit.decorators import ratelimit
import re
import json
import uuid


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
@login_required
def connect_github(request):
    """create a new container collection based on connecting GitHub."""
    if DISABLE_GITHUB:
        messages.info(request, "Making new collections is currently disabled")
        return redirect("collections")

    # All repos owned by the user on GitHub are contenders
    contenders = list_repos(request.user)

    # Filter down to repos that haven't had an equivalent URI added
    # This is intentionally different from the uri that we push so that only
    # builds can be supported from GitHub (and they don't cross contaminate)
    collections = [x.name for x in Collection.objects.filter(owners=request.user)]

    # Only requirement is that URI (name) isn't already taken, add to repos
    repos = []
    for repo in contenders:
        if repo["full_name"] not in collections:
            repos.append(repo)

    context = {"repos": repos}
    return render(request, "google_build/add_collection.html", context)


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
@login_required
def save_collection(request):
    """save the newly selected collection by the user."""
    if DISABLE_GITHUB:
        messages.info(request, "Making new collections is currently disabled")
        return redirect("collections")

    if request.method == "POST":

        # The checked repos are sent in format REPO_{{ repo.owner.login }}/{{ repo.name }}
        repos = [
            x.replace("REPO_", "")
            for x in request.POST.keys()
            if re.search("^REPO_", x)
        ]
        secret = str(uuid.uuid4())
        webhook_secret = str(uuid.uuid4())

        if repos:

            # If the user doesn't have permission to create a collection
            if not request.user.has_create_permission():
                messages.error(
                    request, "You do not have permission to create a collection."
                )
                return redirect("collections")

            # Always just take the first one
            username, reponame = repos[0].split("/")

            # Retrieve the repo fully
            repo = get_repo(request.user, reponame=reponame, username=username)

            # Collection needs to exist before webhook
            collection = Collection.objects.create(
                secret=secret, name=repo["full_name"]
            )

            collection.metadata["github"] = {"secret": webhook_secret}
            collection.metadata["github"].update(update_webhook_metadata(repo))
            collection.save()

            webhook = create_webhook(
                user=request.user, repo=repo, secret=webhook_secret
            )

            if "errors" in webhook:

                # If there is an error, we should tell user about it
                message = ",".join([x["message"] for x in webhook["errors"]])
                messages.info(request, "Errors: %s" % message)

            # If the webhook was successful, it will have a ping_url
            elif "ping_url" in webhook:

                # Add minimal metadata about repo and webhook
                collection.metadata["github"]["webhook"] = webhook

                collection.owners.add(request.user)

                # Add tags
                if "topics" in webhook:
                    if webhook["topics"]:
                        for topic in webhook["topics"]:
                            collection.tags.add(topic)
                        collection.save()

                collection.save()  # probably not necessary
                return redirect(collection.get_absolute_url())

    return redirect("collections")


class RecipePushSerializer(serializers.HyperlinkedModelSerializer):

    created = serializers.DateTimeField(read_only=True)
    collection = serializers.CharField(read_only=True)
    tag = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    owner_id = serializers.CharField(read_only=True)
    datafile = serializers.FileField(read_only=True)

    class Meta:
        model = RecipeFile
        fields = ("created", "datafile", "collection", "owner_id", "tag", "name")


class RecipePushViewSet(ModelViewSet):
    """pushing a recipe coincides with doing a remote build."""

    queryset = RecipeFile.objects.all()
    serializer_class = RecipePushSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):

        print(self.request.data)
        tag = self.request.data.get("tag", "latest")
        name = self.request.data.get("name")
        auth = self.request.META.get("HTTP_AUTHORIZATION", None)
        collection_name = self.request.data.get("collection")

        # Building is disabled
        if DISABLE_BUILDING:
            raise PermissionDenied(detail="Building is disabled.")

        # Authentication always required for push

        if auth is None:
            print("auth is None")
            raise PermissionDenied(detail="Authentication Required")

        owner = get_request_user(auth)
        timestamp = generate_timestamp()
        payload = "build|%s|%s|%s|%s|" % (collection_name, timestamp, name, tag)

        # Validate Payload
        if not validate_request(auth, payload, "build", timestamp):
            print("auth is not valid for build")
            raise PermissionDenied(detail="Unauthorized")

        # Does the user have create permission?
        if not owner.has_create_permission():
            print("owned doesnt have create permission")
            raise PermissionDenied(detail="Unauthorized Create Permission")

        # Are we over the build limit?
        if is_over_limit():
            message = (
                "Registry concurrent build limit is "
                + "%s" % SREGISTRY_GOOGLE_BUILD_LIMIT
                + ". Please try again later."
            )
            print(message)
            raise PermissionDenied(detail=message)

        create_new = False

        # Determine the collection to build the recipe to
        try:
            collection = Collection.objects.get(name=collection_name)

            # Only owners can push to existing collections
            if not owner in collection.owners.all():
                print("user not in owners")
                raise PermissionDenied(detail="Unauthorized")

        except Collection.DoesNotExist:
            print("collection does not exist")
            raise PermissionDenied(detail="Not Found")

        # Validate User Permissions
        if not has_permission(auth, collection, pull_permission=False):
            print("user does not have permissions.")
            raise PermissionDenied(detail="Unauthorized")

        # The collection must exist when we get here
        try:
            container = Container.objects.get(collection=collection, name=name, tag=tag)
            if not container.frozen:
                create_new = True

        except Container.DoesNotExist:
            create_new = True

        # Create the recipe to trigger a build
        print(self.request.data.get("datafile"))

        if create_new is True:
            serializer.save(
                datafile=self.request.data.get("datafile"),
                collection=self.request.data.get("collection"),
                tag=self.request.data.get("tag", "latest"),
                name=self.request.data.get("name"),
                owner_id=owner.id,
            )
        else:
            raise PermissionDenied(
                detail="%s is frozen, push not allowed." % container.get_short_uri()
            )


# Receive GitHub and Google Hooks


@csrf_exempt
def receive_build(request, cid):
    """receive_build will receive the post from Google Cloud Build.
    we check the response header against the jwt token to authenticate,
    and then check other metadata and permissions in complete_build.
    """
    print(request.body)
    print(cid)

    if DISABLE_BUILD_RECEIVE:
        print("DISABLE_BUILD_RECEIVE is active.")
        return JsonResponseMessage(message="Building receive is disabled.")

    if request.method == "POST":

        # Must be an existing container
        container = get_container(cid)
        if container is None:
            return JsonResponseMessage(message="Invalid request.")

        # Decode parameters
        params = json.loads(request.body.decode("utf-8"))

        # Must include a jwt token that is valid for the container
        if not validate_jwt(container, params):
            return JsonResponseMessage(message="Invalid request.")

        scheduler = django_rq.get_scheduler("default")
        scheduler.enqueue_in(
            timedelta(seconds=10), complete_build, cid=container.id, params=params
        )

        return JsonResponseMessage(
            message="Notification Received", status=200, status_message="Received"
        )

    return JsonResponseMessage(message="Invalid request.")


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
@login_required
def delete_container(request, cid):
    """delete a container, including it's corresponding files
    that are stored in Google Build (if they exist)
    """
    container = get_container(cid)

    if not container.has_edit_permission(request):
        messages.info(request, "This action is not permitted.")
        return redirect("collections")

    # Send a job to the worker to delete the build files
    django_rq.enqueue(delete_build, cid=container.id)
    messages.info(request, "Container successfully deleted.")
    return redirect(container.collection.get_absolute_url())


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
@login_required
def delete_collection(request, cid):
    """delete a container collection that has Google Builds

    Parameters
    ==========
    cid: the collection id to delete
    """
    if not _delete_collection(request, cid):
        messages.info(request, "This action is not permitted.")
        return redirect("collections")

    messages.info(request, "Collection requested for deletion.")
    return redirect("collections")


def _delete_collection(request, cid):
    """the underlying function to delete a collection, returns True/False
    if done to the calling view.

    Parameters
    ==========
    cid: the collection id to delete
    """
    collection = get_collection(cid)

    # Only an owner can delete
    if not collection.has_edit_permission(request):
        return False

    # Queue the job to delete the collection
    django_rq.enqueue(
        delete_container_collection, cid=collection.id, uid=request.user.id
    )
    return True


@csrf_exempt
def receive_hook(request):
    """receive_hook will forward a hook to the correct receiver depending on
    the header information. If it cannot be determined, it is ignored.
    """
    if request.method == "POST":

        # Has to have Github-Hookshot
        if re.search("GitHub-Hookshot", request.META["HTTP_USER_AGENT"]) is not None:
            return receive_github_hook(request)

    return JsonResponseMessage(message="Invalid request.")
