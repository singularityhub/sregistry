'''

Copyright (C) 2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from shub.logger import bot
from django.conf import settings                                                  
from django.core.exceptions import ObjectDoesNotExist
from shub.apps.users.models import User
from shub.apps.main.models import Container, Collection
from shub.apps.main.views import update_container_labels
from sregistry.main.google_build.client import get_client 
from pathlib import Path
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
        container= collection.containers.get(tag=instance.tag, 
                                             name=instance.name)

    except ObjectDoesNotExist:
        container = Container.objects.create(collection=collection,
                                             tag=instance.tag,
                                             name=instance.name)

    # Add the metadata
    container.metadata['build_metadata'] = response['metadata']
    container.metadata['builder'] = "google_build"
    container.save()


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
        container.metadata['builder'] = "google_build"
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


def complete_build(container):
    '''finish a build, meaning obtaining the original build_id for the container
       and checking for completion.

       Parameters
       ==========
       container: the container to finish the build for, expected to have an id
    '''
    context = get_build_context()

    # Instantiate client with context (connects to buckets)
    client = get_client(debug=True, **context)

    build_id = container.metadata['build_metadata']['id']
    response = client.finish_build(build_id)
    import pickle
    pickle.dump(response, open('build-response.pkl', 'wb'))
    print(response)
