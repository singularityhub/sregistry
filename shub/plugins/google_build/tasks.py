'''

Copyright (C) 2016-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from celery import shared_task, Celery
from django.conf import settings
#from shub.apps.api.build.google import delete_storage_files
from django.contrib.auth.decorators import login_required

from background_task import background
from dateutil.parser import parse
import os
import re

from django.conf import settings
from django.apps import apps

#app = Celery('shub')
#app.config_from_object('django.conf:settings', namespace="CELERY")
#app.conf.imports = settings.CELERY_IMPORTS
#app.autodiscover_tasks(lambda: [a.name for a in apps.get_app_configs()])

@background(schedule=1)
def prepare_build_task(cid, recipes, branch):
    '''wrapper to prepare build, to run as a task

       Parameters
       ==========
       cid: the collection id to retrieve the collection
       recipes: a dictionary of modified recipe files to build
       branch: the repository branch (kept as metadata)
    '''
    print('RUNNING PREPARE BUILD TASK WITH RECIPES %s' %recipes)
    from .actions import receive_build
    from shub.apps.main.views import get_collection
    collection = get_collection(cid)
    receive_build(collection=collection,
                  recipes=recipes,
                  branch=branch)


@shared_task
def run_delete_storage_files(files):
    '''A task to delete a set of files in a storage bucket
       TODO: need to write this.
    '''
    if len(files) > 0:
        print("Deleting storage files for %s files" %(len(files)))
        delete_storage_files(files)


@background(schedule=1)
def parse_hook(cid, 
               branch="master",
               commits=None):

    '''parse hook will take a request and an associated user collection, 
       and finish parsing. This means generating the new container, 
       and submitting a job to run on Google Cloud Build.
    '''
    from .github import get_commit_details, get_commit_date
    from shub.apps.main.views import get_collection

    print("RUNNING PARSE HOOK")
    collection = get_collection(cid)

    # Determine changed Singularity file(s)
    if commits is None:
        commits = get_commit_details(collection, limit=25)

    modified = dict()
    renamed = []

    # Find changed files!
    for commit in commits:

        commit_id = commit.get('sha') or commit.get('id')
        commit_date = commit['commit']['committer']['date']

        for record in commit['files']:

            # The file could have been removed
            if record['status'] == 'removed':
                add_record = False
                remove_record = True

            # Only going to build updated recipes
            elif record['status'] in ['added', 'modified', 'renamed']:

                # Supports building from Singularity recipes
                if re.search("Singularity", record['filename']):
                    add_record = True
                    remove_record = False

                    # If the record is renamed after in modified, don't add
                    if record['status'] == 'renamed':
                        renamed.append({"to": record['filename'],
                                        "from": record['previous_filename'],
                                        "date": commit_date})

                    if record['filename'] in modified:

                        # Don't add if we have more recent
                        if parse(commit_date) < parse(modified[record['filename']]['date']): 
                            add_record = False

            # Do we add or remove?
            if add_record:
                modified[record['filename']] = {
                                'url': commit['url'],
                                'commit': commit_id,
                                'date': commit_date,
                                'name': collection.metadata['github']['repo_name']}

            elif remove_record and record in modified:
                del modified[record]

    print("MODIFIED RECIPES BEFORE RENAME %s" % modified)

    # If the previous filename date is later than the record
    for entry in renamed:

        # If the entry was modified before it was renamed, remove it
        if entry['from'] in modified: 
            if parse(modified[entry['from']]['date']) < parse(entry['date']):
                del modified[entry['from']]

    print("MODIFIED RECIPES AFTER RENAME %s" % modified)

    # If we have records after parsing
    if modified:

        kwargs = kwargs={"cid": collection.id,
                         "recipes": modified,
                         "branch": branch}

        print(kwargs)

        # This function submits the google build
        prepare_build_task.apply_async(kwargs=kwargs)
