'''

Copyright (C) 2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from shub.logger import bot
from dateutil.parser import parse
from django.conf import settings                                                  
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from shub.apps.users.models import User
from shub.apps.main.models import Container, Collection
from shub.apps.main.views import update_container_labels
from sregistry.main.google_build.client import get_client 
from datetime import datetime
from pathlib import Path
from .utils import (
    convert_size, 
    JsonResponseMessage
)
from .utils import 
import os


def trigger_build(sender, instance, **kwargs):
    '''Trigger build will send a recipe directly to Google Cloud Build,
       and create a container that will send a curl response back to
       an endpoint here to signal that the build is complete. 
       Triggered by RecipePushSerializer.

       Parameters
       ==========
       sender: should be the sending model, which is an RecipeFile instance
       instance: is the instance of the RecipeFile
    '''
    collection = Collection.objects.get(name=instance.collection)
    context = get_build_context()

    # Instantiate client with context (connects to buckets)
    client = get_client(debug=True, **context)

    # Assemble the name
    name = "%s/%s:%s" %(instance.collection, instance.name, instance.tag)

    # The recipe needs to be in PWD to create the build package
    recipe = os.path.basename(instance.datafile.name)
    os.chdir(os.path.dirname(instance.datafile.name))
    
    # Submit the build
    response = client.build(name, 
                            recipe=recipe,
                            headless=True,
                            webhook=reverse('receive_build', {"cid": container.id}))

    # Create a container (with status google-build) for the user to watch
    try:
        container = collection.containers.get(tag=instance.tag, 
                                             name=instance.name)

    except ObjectDoesNotExist:
        container = Container.objects.create(collection=collection,
                                             tag=instance.tag,
                                             name=instance.name)

    # If the container is frozen, no good.
    if not container.frozen:
        
        # Add the metadata
        container.metadata['build_metadata'] = response['metadata']
        container.metadata['builder'] = {"name": "google_build"}
        container.save()
    
    else:
        bot.warning('%s is frozen, will not trigger build.' % container)


def receive_build(collection, recipes, branch):
    '''receive_build will receive a build from GitHub, and then trigger
       the same Google Cloud Build but using a GitHub repository (recommended).

       Parameters
       ==========
       collection: the collection
       recipes: a dictionary of modified recipe files to build
       branch: the repository branch (kept as metadata)
    '''
    context = get_build_context()

    # Instantiate client with context (connects to buckets)
    client = get_client(debug=True, **context)

    print("RECIPES: %s" % recipes)

    # Derive tag from the recipe, or default to latest
    for recipe, metadata in recipes.items():

        # First preference to command line, then recipe tag
        tag = "".join(Path(recipe).suffixes).strip('.')
        tag = (tag or "latest").strip('.')

        # Get a container, if it exists, we've already written file here
        try:
            container = collection.containers.get(tag=tag)
        except: # DoesNotExist
            container = Container.objects.create(collection=collection,
                                                 tag=tag,
                                                 name=collection.name)

        # If the container is frozen, no go
        if container.frozen:
            bot.debug('%s is frozen, will not trigger build.' % container)
            continue

        # Recipe path on Github
        reponame = container.collection.metadata['github']['repo_name']

        # If we don't have a commit, just send to recipe
        if metadata['commit'] is None:
            deffile = "https://www.github.com/%s/tree/%s/%s" %(reponame,
                                                               branch,
                                                               recipe)
        else:
            deffile = "https://www.github.com/%s/blob/%s/%s" %(reponame,
                                                               metadata['commit'],
                                                               recipe)
        # Webhook response
        webhook = "%s%s" % (settings.DOMAIN_NAME,
            reverse('receive_build', kwargs={"cid": container.id}))

        # Submit the build with the GitHub repo and commit
        response = client.build_repo("github.com/%s" % metadata['name'], 
                                      recipe=recipe,
                                      headless=True,
                                      commit=metadata['commit'],
                                      webhook=webhook)

        # Add the metadata
        container.metadata['build_metadata'] = response['metadata']
        container.metadata['builder'] = {"name":"google_build",
                                         "deffile": deffile}
        container.save()


def get_build_context():
    '''get shared build context between recipe build (push of a recipe) and
       GitHub triggered build. This function takes no arguments
    '''
    # We checked that the setting is defined, here ensure exists
    if not os.path.exists(settings.GOOGLE_APPLICATION_CREDENTIALS):
        bot.exit('%s does not exist.' % settings.GOOGLE_APPLICATION_CREDENTIALS)

    # Provide all envars directly to client instead of environment
    context = {'GOOGLE_APPLICATION_CREDENTIALS': settings.GOOGLE_APPLICATION_CREDENTIALS,
               'SREGISTRY_GOOGLE_PROJECT': settings.SREGISTRY_GOOGLE_PROJECT}

    # Put the credentials in the environment to find
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.GOOGLE_APPLICATION_CREDENTIALS

    # The following are optional
    for attr in ['SREGISTRY_GOOGLE_BUILD_CACHE',
                 'SREGISTRY_GOOGLE_BUILD_SINGULARITY_VERSION',
                 'SREGISTRY_GOOGLE_STORAGE_PRIVATE',
                 'SREGISTRY_GOOGLE_STORAGE_BUCKET']:
        if hasattr(settings, attr):
            context[attr] = getattr(settings, attr)
    return context


def complete_build(container, params):
    '''finish a build, meaning obtaining the original build_id for the container
       and checking for completion.

       Parameters
       ==========
       container: the container to finish the build for, expected to have an id
       params: the parameters from the build. They must have matching build it.
    '''
    # Case 1: No id provided
    if "id" not in params:
        return JsonResponseMessage(message="Invalid request.")

    # Case 2: the container is already finished or not a google build
    if "build_metadata" not in container.metadata or "builder" not in container.metadata:
        return JsonResponseMessage(message="Invalid request.")

    # Case 3: It's not a Google Build
    if container.metadata['builder'].get('name') != "google_build":
        return JsonResponseMessage(message="Invalid request.")

    # Google build will have an id here
    build_id = container.metadata['build_metadata']['build']['id']

    # Case 4: Build is already finished
    active = ["QUEUED", "RUNNING"]
    if build_id not in active:
        return JsonResponseMessage(message="Invalid request.")

    # Case 5: Build id doesn't match
    if build_id != params['id']:
        return JsonResponseMessage(message="Invalid request.")

    context = get_build_context()

    # Instantiate client with context (connects to buckets)
    client = get_client(debug=True, **context)
    
    # Get an updated status
    response = client._finish_build(build_id)

    if "public_url" in response:
        container.metadata['image'] = response['public_url']
    else:
        container.metadata['image'] = response['media_link']

    # Save the build finish
    container.metadata['build_finish'] =  response

    # Add response metrics (size and file_hash)
    if "size" in response:
        container.metrics["size_mb"] = convert_size(response["size"])

    # If a file hash is included, we use this as the version (not commit)
    if "file_hash" in response:
        container.metrics["file_hash"] = response["file_hash"]
        container.version = response['file_hash'] 
 
    # Calculate total time
    if "startTime" in response and "finishTime" in response:
        total_time = parse(response['finishTime']) - parse(response['startTime'])
        container.metrics['build_seconds'] = total_time.total_seconds()

    # Created date
    if "createTime" in response:
        created_at = datetime.strftime(parse(response['createTime']), '%h %d, %Y')
        container.metrics['created_at'] = created_at

    container.save()
    return JsonResponseMessage(message="Notification Received",
                               status=200,
                               status_message="Received")
