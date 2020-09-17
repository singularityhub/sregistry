"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from dateutil.parser import parse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from shub.logger import bot
from shub.apps.main.models import Container, Collection
from sregistry.main.google_build.client import get_client
from datetime import datetime, timedelta
from sregistry.utils import get_recipe_tag
from .utils import (
    convert_size,
    clear_container_payload,
    create_container_payload,
    JsonResponseMessage,
    generate_jwt_token,
)
import os
import django_rq


def trigger_build(sender, instance, **kwargs):
    """Trigger build will send a recipe directly to Google Cloud Build,
    and create a container that will send a curl response back to
    an endpoint here to signal that the build is complete.
    Triggered by RecipePushSerializer.

    Parameters
    ==========
    sender: should be the sending model, which is an RecipeFile instance
    instance: is the instance of the RecipeFile
    """
    collection = Collection.objects.get(name=instance.collection)
    context = get_build_context()

    print("IN TRIGGER BUILD")

    # Instantiate client with context (connects to buckets)
    client = get_client(debug=True, **context)

    # Assemble the name
    name = "%s/%s:%s" % (instance.collection, instance.name, instance.tag)

    # The recipe needs to be in PWD to create the build package
    recipe = instance.datafile.name
    working_dir = os.path.dirname(recipe)

    # Create a container (with status google-build) for the user to watch
    try:
        container = collection.containers.get(tag=instance.tag, name=instance.name)

    except ObjectDoesNotExist:
        container = Container.objects.create(
            collection=collection, tag=instance.tag, name=instance.name
        )

    # If it's frozen, don't submit
    if container.frozen:
        return JsonResponseMessage(message="Container is frozen.")

    # Webhook response
    webhook = "%s%s" % (
        settings.DOMAIN_NAME,
        reverse("receive_build", kwargs={"cid": container.id}),
    )

    # Generate a one time use secret for jwt web token
    container.metadata["builder"] = {"name": "google_build"}

    payload = create_container_payload(container)  # does not save

    # Generate the jwt token
    jwt_token = generate_jwt_token(
        secret=container.metadata["builder"]["secret"], payload=payload
    )

    # Submit the build
    response = client.build(
        name,
        recipe=recipe,
        working_dir=working_dir,
        headless=True,
        webhook=webhook,
        extra_data={"token": jwt_token},
    )

    # Update the status for the container
    if "status" in response:
        container.metadata["build_metadata"]["build"]["status"] = response["status"]

    # Add the metadata
    container.metadata["build_metadata"] = response["metadata"]
    container.save()

    print(response)
    return JsonResponseMessage(message="Build received.")


def receive_build(collection, recipes, branch):
    """receive_build will receive a build from GitHub, and then trigger
    the same Google Cloud Build but using a GitHub repository (recommended).

    Parameters
    ==========
    collection: the collection
    recipes: a dictionary of modified recipe files to build
    branch: the repository branch (kept as metadata)
    """
    from .github import get_auth_token

    context = get_build_context()

    # Instantiate client with context (connects to buckets)
    client = get_client(debug=True, **context)

    print("RECIPES: %s" % recipes)

    # Derive tag from the recipe, or default to latest
    for recipe, metadata in recipes.items():

        # First preference to command line, then recipe tag
        tag = get_recipe_tag(recipe) or "latest"

        # Get a container, if it exists, we've already written file here
        try:
            container = collection.containers.get(tag=tag)
        except:  # DoesNotExist
            container = Container.objects.create(
                collection=collection, tag=tag, name=collection.name
            )

        # If the container is frozen, no go
        if container.frozen:
            bot.debug("%s is frozen, will not trigger build." % container)
            continue

        # Recipe path on Github
        reponame = container.collection.metadata["github"]["repo_name"]

        # If we don't have a commit, just send to recipe
        if metadata["commit"] is None:
            deffile = "https://www.github.com/%s/tree/%s/%s" % (
                reponame,
                branch,
                recipe,
            )
        else:
            deffile = "https://www.github.com/%s/blob/%s/%s" % (
                reponame,
                metadata["commit"],
                recipe,
            )
        # Webhook response
        webhook = "%s%s" % (
            settings.DOMAIN_NAME,
            reverse("receive_build", kwargs={"cid": container.id}),
        )

        # Generate a one time use secret for jwt web token
        container.metadata["builder"] = {"name": "google_build", "deffile": deffile}

        payload = create_container_payload(container)  # does not save

        # Generate the jwt token
        jwt_token = generate_jwt_token(
            secret=container.metadata["builder"]["secret"], payload=payload
        )

        # If the repo is private, we need to account for that
        token = None
        if collection.metadata["github"].get("private", False) is True:
            token = get_auth_token(collection.owners.first())

        # Submit the build with the GitHub repo and commit
        response = client.build_repo(
            "github.com/%s" % metadata["name"],
            recipe=recipe,
            headless=True,
            token=token,
            commit=metadata["commit"],
            webhook=webhook,
            extra_data={"token": jwt_token},
        )

        # Add the metadata
        container.metadata["build_metadata"] = response["metadata"]
        container.save()


def get_build_context():
    """get shared build context between recipe build (push of a recipe) and
    GitHub triggered build. This function takes no arguments.
    """
    # We checked that the setting is defined, here ensure exists
    if not os.path.exists(settings.GOOGLE_APPLICATION_CREDENTIALS):
        bot.exit("%s does not exist." % settings.GOOGLE_APPLICATION_CREDENTIALS)

    # Provide all envars directly to client instead of environment
    context = {
        "GOOGLE_APPLICATION_CREDENTIALS": settings.GOOGLE_APPLICATION_CREDENTIALS,
        "SREGISTRY_GOOGLE_PROJECT": settings.SREGISTRY_GOOGLE_PROJECT,
    }

    # Put the credentials in the environment to find
    os.environ[
        "GOOGLE_APPLICATION_CREDENTIALS"
    ] = settings.GOOGLE_APPLICATION_CREDENTIALS

    # The following are optional
    for attr in [
        "SREGISTRY_GOOGLE_BUILD_CACHE",
        "SREGISTRY_GOOGLE_BUILD_SINGULARITY_VERSION",
        "SREGISTRY_GOOGLE_STORAGE_BUCKET",
    ]:
        if hasattr(settings, attr):
            context[attr] = getattr(settings, attr)
    return context


def delete_build(cid, client=None):
    """Delete artifacts for a container build, if they exist, along
    with the container object. This is called
    as a django-rq task for a worker to do from views.py

    Parameters
    ==========
    cid: the container id to finish the build for, expected to have an id
    """
    from shub.apps.main.views import get_container

    container = get_container(cid)

    # if being called from delete_container_collection, just instantiate once
    if client is None:
        context = get_build_context()
        client = get_client(debug=True, **context)

    # If the container has an image, delete it
    image = container.get_image() or ""

    is_google_build = False
    if "builder" in container.metadata:
        if "name" in container.metadata["builder"]:
            if container.metadata["builder"]["name"] == "google_build":
                is_google_build = True

    # Case 1: A google build
    if is_google_build:
        if "storage.googleapis.com" in image:
            print("deleting container %s" % image)
            container_name = os.path.basename(image)
            client.delete(container_name, force=True)

    # Finally, delete the container
    container.delete()


def delete_container_collection(cid, uid):
    """Delete artifacts for a container build, if they exist, and then
    the entire collection. This is called
    as a django-rq task for a worker to do from views.py

    Parameters
    ==========
    cid: the collection id to delete.
    uid: the user id requesting permission
    """
    from shub.apps.main.views import get_collection
    from .github import delete_webhook

    collection = get_collection(cid)

    # Delete files before containers
    containers = Container.objects.filter(collection=collection)

    # Create a client to share
    context = get_build_context()
    client = get_client(debug=True, **context)

    # Delete container build objects first
    for container in containers:
        delete_build(cid=container.id, client=client)

    # Now handle the webhook (a separate task)
    if "github" in collection.metadata:
        django_rq.enqueue(
            delete_webhook,
            user=uid,
            repo=collection.metadata["github"]["repo_name"],
            hook_id=collection.metadata["github"]["webhook"]["id"],
        )

    # Finally, delete the collection
    print("%s deleting." % collection)
    collection.delete()


def is_over_limit(limit=None):
    """check if we are over the limit for active builds. Returns a boolean to
    indicate yes or no, based on filtering the number of total builds
    by those with status "QUEUED" or "WORKING."

    Parameters
    ==========
    limit: an integer limit for the maximum concurrent waiting or active
           builds. If not set, we use the default in settings.
    """
    # Allow the function to set a custom limit
    limit = limit or settings.SREGISTRY_GOOGLE_BUILD_LIMIT

    # Instantiate client with context (connects to buckets)
    context = get_build_context()
    client = get_client(debug=True, **context)

    project = settings.SREGISTRY_GOOGLE_PROJECT
    result = (
        client._build_service.projects()
        .builds()
        .list(projectId=project, filter='status="QUEUED" OR status="WORKING"')
        .execute()
    )
    return len(result) > limit


def complete_build(cid, params, check_again_seconds=10):
    """finish a build, meaning obtaining the original build_id for the container
    and checking for completion.

    Parameters
    ==========
    cid: the container id to finish the build for, expected to have an id
    params: the parameters from the build. They must have matching build it.
    check_again_seconds: if the build is still working, check again in this
                         many seconds. By default, we multiply by 2 each time
                         (exponential backoff).
    """
    from shub.apps.main.views import get_container

    print("RUNNING COMPLETE BUILD")
    container = get_container(cid)

    # Case 1: No id provided
    if "id" not in params:
        return JsonResponseMessage(message="Invalid request.")

    # Case 2: the container is already finished or not a google build
    if (
        "build_metadata" not in container.metadata
        or "builder" not in container.metadata
    ):
        return JsonResponseMessage(message="Invalid request.")

    # Case 3: It's not a Google Build
    if container.metadata["builder"].get("name") != "google_build":
        return JsonResponseMessage(message="Invalid request.")

    # Google build will have an id here
    build_id = container.metadata["build_metadata"]["build"]["id"]
    status = container.metadata["build_metadata"]["build"]["status"]

    # Case 4: Build is already finished
    active = ["QUEUED", "WORKING"]
    if status not in active:
        return JsonResponseMessage(message="Invalid request.")

    # Case 5: Build id doesn't match
    if build_id != params["id"]:
        return JsonResponseMessage(message="Invalid request.")

    context = get_build_context()

    # Instantiate client with context (connects to buckets)
    client = get_client(debug=True, **context)

    # Get an updated status
    response = client._finish_build(build_id)

    if "public_url" in response:
        container.metadata["image"] = response["public_url"]

    elif "media_link" in response:
        container.metadata["image"] = response["media_link"]

    elif "status" in response:

        # If it's still working, schedule to check with exponential backoff
        if response["status"] in ["QUEUED", "WORKING"]:
            check_again_seconds = check_again_seconds * 2
            print("Build status WORKING: checking in %s seconds" % check_again_seconds)

            # Get the scheduler, submit to check again
            scheduler = django_rq.get_scheduler("default")
            scheduler.enqueue_in(
                timedelta(seconds=check_again_seconds),
                complete_build,
                cid=container.id,
                params=params,
                check_again_seconds=check_again_seconds,
            )

    # This is an invalid status, and no action to take
    else:
        print("Invalid response, no container link and status not working.")
        return

    # Save the build finish
    container.metadata["build_finish"] = response

    # Clear the container metadata
    container = clear_container_payload(container)

    # Add response metrics (size and file_hash)
    if "size" in response:
        container.metrics["size_mb"] = round(convert_size(response["size"], "MB"), 3)

    # Update the status
    if "status" in response:
        container.metadata["build_metadata"]["build"]["status"] = response["status"]

    # If a file hash is included, we use this as the version (not commit)
    if "crc32" in response:
        container.metrics["crc32"] = response["crc32"]

    # Add the version, also calculated by builder
    if "sha256sum" in response:
        container.metrics["sha256"] = "sha256.%s" % response["sha256sum"]
        container.version = "sha256.%s" % response["sha256sum"]

    # Keep an md5, for posterity
    if "md5sum" in response:
        container.metrics["md5"] = "md5.%s" % response["md5sum"]

    # Calculate total time
    if "startTime" in response and "finishTime" in response:
        total_time = parse(response["finishTime"]) - parse(response["startTime"])
        container.metrics["build_seconds"] = total_time.total_seconds()

    # Created date
    if "createTime" in response:
        created_at = datetime.strftime(parse(response["createTime"]), "%h %d, %Y")
        container.metrics["created_at"] = created_at

    container.save()
