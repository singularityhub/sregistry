"""

Copyright (C) 2016-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from dateutil.parser import parse
import django_rq
import os
import re


def prepare_build_task(cid, recipes, branch):
    """wrapper to prepare build, to run as a task

    Parameters
    ==========
    cid: the collection id to retrieve the collection
    recipes: a dictionary of modified recipe files to build
    branch: the repository branch (kept as metadata)
    """
    print("RUNNING PREPARE BUILD TASK WITH RECIPES %s" % recipes)
    from .actions import receive_build
    from shub.apps.main.views import get_collection

    collection = get_collection(cid)
    receive_build(collection=collection, recipes=recipes, branch=branch)


def parse_hook(cid, branch="master", commits=None):

    """parse hook will take a request and an associated user collection,
    and finish parsing. This means generating the new container,
    and submitting a job to run on Google Cloud Build.
    """
    from shub.apps.main.views import get_collection

    print("RUNNING PARSE HOOK")
    collection = get_collection(cid)

    # Determine changed Singularity file(s)
    if commits is None:
        return build_previous_commits(collection, branch)
    return build_commits(collection, commits, branch)


def build_commits(collection, commits, branch):
    """build commits that come directly from a ping. For this version, we get
    a data structure with a list of added, removed, and modified files.

    Parameters
    ==========
    collection: The collection to get details for.
    commits: the commits to build.
    """
    modified = dict()
    removed = []

    # Find changed files!
    for commit in commits:

        print(commit)
        commit_id = commit.get("id")
        commit_date = commit.get("timestamp")
        files = commit["modified"] + commit["added"]

        # Add Removed files to compare with after
        for filename in commit["removed"]:
            removed.append({"name": filename, "id": commit_id, "date": commit_date})

        for filename in files:

            # Supports building from Singularity recipes
            if re.search("Singularity", filename):
                add_record = True

            if filename in modified:

                # Don't add if we have more recent
                if parse(commit_date) < parse(modified[filename]["date"]):
                    add_record = False

            # Do we add or remove?
            if add_record:
                modified[filename] = {
                    "url": commit["url"],
                    "commit": commit_id,
                    "date": commit_date,
                    "name": collection.metadata["github"]["repo_name"],
                }

    print("MODIFIED RECIPES BEFORE RENAME %s" % modified)

    # If the previous filename date is later than the record
    for entry in removed:

        # If the entry was modified before it was removed, remove it
        if entry["name"] in modified:
            if parse(modified[entry["name"]]["date"]) < parse(entry["date"]):
                del modified[entry["name"]]

    print("MODIFIED RECIPES AFTER RENAME %s" % modified)

    # If we have records after parsing
    if modified:

        # This function submits the google build
        django_rq.enqueue(
            prepare_build_task, cid=collection.id, recipes=modified, branch=branch
        )


def build_previous_commits(collection, branch):
    """the result we get when we get commit details (from the API)
    versus an actual commit object is different. This function parses
    the results from "get_commit_details"

    Parameters
    ==========
    collection: The collection to get details for.
    """
    from .github import get_commit_details

    commits = get_commit_details(collection, limit=25)

    modified = []
    renamed = []

    # Find changed files!
    for commit in commits:

        commit_id = commit.get("sha") or commit.get("id")
        commit_date = commit["commit"]["committer"]["date"]

        for record in commit["files"]:

            # We care about absolute basename paths
            filename = record["filename"]

            # The file could have been removed
            if record["status"] == "removed":
                continue

            # Only going to build updated recipes
            elif record["status"] in ["added", "modified", "renamed"]:

                # Supports building from Singularity recipes
                if re.search("Singularity", filename):

                    # If the record is renamed after in modified, don't add
                    if record["status"] == "renamed":
                        renamed.append(
                            {
                                "to": record["filename"],
                                "from": record["previous_filename"],
                                "date": commit_date,
                            }
                        )

                    # The same file
                    elif record["status"] in ["added", "modified"]:
                        modified.append(
                            {
                                "url": commit["url"],
                                "commit": commit_id,
                                "recipe": record["filename"],
                                "date": commit_date,
                                "name": collection.metadata["github"]["repo_name"],
                            }
                        )

    # Now assemble keepers
    keepers = {}
    for entry in modified:

        # The recipe is what we compare to
        recipe = os.path.basename(entry["recipe"])
        if recipe in keepers:

            # Update if it's more recent
            if parse(keepers[recipe]["date"]) < parse(entry["date"]):
                keepers[recipe] = entry

        else:
            keepers[recipe] = entry

    # Change the recipe index back to the correct filename
    modified = {}
    for recipe, metadata in keepers.items():
        modified[metadata["recipe"]] = metadata

    # If the previous filename date is later than the record
    for entry in renamed:

        # If the entry was modified before it was renamed, remove it
        if entry["from"] in modified:
            if parse(modified[entry["from"]]["date"]) < parse(entry["date"]):
                del modified[entry["from"]]

    print("MODIFIED RECIPES AFTER RENAME %s" % modified)

    # If we have records after parsing
    if modified:

        # This function submits the google build
        django_rq.enqueue(
            prepare_build_task, cid=collection.id, recipes=modified, branch=branch
        )
