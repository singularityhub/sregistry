"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

import django_rq

from shub.apps.users.models import User
from shub.logger import bot
from shub.settings import (
    DISABLE_GITHUB,
    DISABLE_BUILDING,
    DOMAIN_NAME,
    SREGISTRY_GOOGLE_BUILD_LIMIT,
)
from shub.apps.main.models import Collection

from .utils import (
    check_headers,
    get_default_headers,
    JsonResponseMessage,
    load_body,
    paginate,
    validate_payload,
    DELETE,
    POST,
)

from dateutil.parser import parse
from datetime import datetime
import re
import requests


api_base = "https://api.github.com"


## Calls


def get_auth(user, headers=None, idx=0):
    """get_auth will return the authentication header for a user
    the default headers (without auth) are returned if provider not github

    Parameters
    ==========
    user: a user object
    """
    if headers is None:
        headers = get_default_headers()

    # Tasks might provide a user id instead
    if not isinstance(user, User):
        try:
            user = User.objects.get(id=user)
        except User.DoesNotExist:
            pass

    token = get_auth_token(user, idx)

    if token is not None:
        token = "token %s" % (token)
        headers["Authorization"] = token
    return headers


def get_auth_token(user, idx=0):
    """get_auth_token will return the auth token for a user.

    Parameters
    ==========
    user: a user object
    """
    # 1. Github private first priority
    auth = [x for x in user.social_auth.all() if x.provider == "github-private"]

    # 2. Github public second priority
    if not auth:
        auth = [x for x in user.social_auth.all() if x.provider == "github"]

    if len(auth) > idx:
        return auth[idx].access_token
    else:
        return auth[0].access_token


def get_repo(user, reponame, username, headers=None):
    """get_repo will return a single repo, username/reponame
    given authentication with user

    Parameters
    ==========
    user: the user to get github credentials for
    reponame: the name of the repo to retrieve
    username: the username of the repo (owner)
    """
    # Case 1, the user just has one auth or just public
    if headers is None:
        headers = get_auth(user)
    headers["Accept"] = "application/vnd.github.mercy-preview+json"
    url = "%s/repos/%s/%s" % (api_base, username, reponame)
    response = requests.get(url, headers=headers)

    # Case 2: public and private
    if response.status_code != 200:
        auth_headers = get_auth(user, idx=1)
        headers.update(auth_headers)
        response = requests.get(url, headers=headers)
    response = response.json()
    return response


def list_repos(user, headers=None):
    """list_repos will list the public repos for a user

    Parameters
    ==========
    user: a user object to list
    headers: headers to replace default
    """
    if headers is None:
        headers = get_auth(user)
    url = "%s/user/repos" % (api_base)
    repos = paginate(url=url, headers=headers)

    if not repos:
        auth_headers = get_auth(user, idx=1)
        headers.update(auth_headers)
        repos = paginate(url=url, headers=headers)
    return repos


def get_commits(user, uri, headers=None, sha=None, limit=None):
    """list_repos will list the public repos for a user

    Parameters
    ==========
    user: the user that owns the repository
    uri: the username/repo
    page: the page of results to return, if none, paginates
    """
    if not headers:
        headers = get_auth(user)
    headers["Accept"] = "application/vnd.github.cryptographer-preview"
    url = "%s/repos/%s/commits" % (api_base, uri)

    # Option 1: return a sha
    if sha:
        url = "%s/%s" % (url, sha)
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            headers.update(get_auth(user, idx=1))
            response = requests.get(url, headers=headers)
        return [response.json()]

    # Option 2, return paginated commits
    commits = paginate(url=url, headers=headers, limit=limit)
    if not commits:
        auth_headers = get_auth(user, idx=1)
        headers.update(auth_headers)
        commits = paginate(url=url, headers=headers, limit=limit)
    bot.debug("Found %s commits" % len(commits))
    return commits


def get_branch_commits(user, uri, branch):
    """get all commits for a particular branch"""
    headers = get_auth(user)
    headers["Accept"] = "application/vnd.github.cryptographer-preview"
    url = "%s/repos/%s/commits?sha=%s" % (api_base, uri, branch)
    response = requests.get(url=url, headers=headers)
    if response.status_code != 200:
        auth_headers = get_auth(user, idx=1)
        headers.update(auth_headers)
        response = requests.get(url=url, headers=headers)
    return response.json()


def get_commit_date(commit):
    """return the commit author date, then the committer"""
    return commit["commit"].get("author").get("date") or commit["commit"].get(
        "committer"
    ).get("date")


def get_commits_since(commits, since):
    """from a list of commits, return those in a list that occured since
    a provided date (since)
    """
    updates = []
    seen = []

    def isnew(changed, since):
        if isinstance(since, int):
            since = datetime.fromtimestamp(since).strftime("%Y-%m-%dT%H:%M:%SZ")
        if parse(changed) >= parse(since):
            return True
        return False

    for commit in commits:
        commit_date = get_commit_date(commit)
        if isnew(commit_date, since) and commit["sha"] not in seen:
            updates.append(commit)
            seen.append(commit["sha"])

    return updates


def get_commit_details(collection, since=None, headers=None, limit=None):
    """get changed files will find changed files since a particular date.
    If since is not defined, we take the following logic:

    1. First compare the commits date against the repo pushed_date. If
       commits are found, differences are determined between those ranges.
    2. If the webhook was created without a new commit/push, then fall back
       to comparing commits to the webhook creation date
    3. If still no passing ranges, parse entire result for changed files,
       and return the most recent of each.
    """
    if since is None:
        since = collection.metadata["github"]["pushed_at"]
    commits = get_commits(
        user=collection.owners.first(),  # user created repo
        uri=collection.metadata["github"]["repo_name"],
        limit=limit,
    )

    # If the collection has no containers, assess all commits
    if not collection.containers.count():
        updates = commits
    else:
        # First pass, commit date vs. repo[pushed_at]
        updates = get_commits_since(commits, since)

    # Second pass, commit date vs. webhook[created_at]
    if not updates:
        since = collection.metadata["github"]["webhook"]["created_at"]
        updates = get_commits_since(commits, since)

    # Last try, since repo created
    if not updates:
        since = collection.metadata["github"]["created_at"]
        updates = get_commits_since(commits, since)

    commits = []

    # Retrieve commits with complete list of changes
    for commit in updates:
        response = get_commits(
            user=collection.owners.first(),
            uri=collection.metadata["github"]["repo_name"],
            sha=commit["sha"],
        )
        if response:
            commits = commits + response
    return commits


## Create


def create_webhook(user, repo, secret):
    """create_webhook will create a webhook for a repo to send back
    to singularity hub on push

    Parameters
    ==========
    user: user: should be a singularity hub user. This is used to get
                the Github authentication
    repo: should be a complete repo object, including username and reponame
    secret: should be a randomly generated string, created when repo connected,
            to validate future pushes
    """
    headers = get_auth(user)

    url = "%s/repos/%s/hooks" % (api_base, repo["full_name"])

    callback_url = "%s%s/" % (DOMAIN_NAME.strip("/"), reverse("receive_hook"))

    config = {"url": callback_url, "content_type": "json", "secret": secret}

    params = {
        "name": "web",
        "active": True,
        "events": ["push", "deployment"],
        "config": config,
    }

    # Create webhook
    response = POST(url, headers=headers, data=params)
    if response.status_code != 201:
        headers.update(get_auth(user, idx=1))
        response = POST(url, headers=headers, data=params)

    response = response.json()

    # Get topics
    full_repo = get_repo(
        user=user,
        headers=headers,
        reponame=repo["name"],
        username=repo["owner"]["login"],
    )

    response["topics"] = []
    if "topics" in full_repo:
        response["topics"] = full_repo["topics"]

    return response


def update_webhook_metadata(repo):
    """based on a repository field from a webhook payload, return an
    updated data structure with fields that we care about.

    Parameters
    ==========
    repo: the repository object to get fields from
    """
    return {
        "repo": repo["clone_url"],
        "private": repo["private"],
        "description": repo["description"],
        "created_at": repo["created_at"],
        "updated_at": repo["updated_at"],
        "pushed_at": repo["pushed_at"],
        "repo_id": repo["id"],
        "repo_name": repo["full_name"],
    }


## Delete


def delete_webhook(user, repo, hook_id):
    """delete_webhook will delete a webhook, done when a user deletes a collection.
    https://developer.github.com/v3/repos/hooks/#delete-a-hook
    DELETE /repos/:owner/:repo/hooks/:hook_id

    Parameters
    ==========
    user: should be a singularity hub user. This is used to get
          the Github authentication
    repo: should be a complete repo object, including username and reponame
    """
    headers = get_auth(user)

    url = "%s/repos/%s/hooks/%s" % (api_base, repo, hook_id)

    response = DELETE(url, headers)
    if response.status_code != 200:
        headers.update(get_auth(user, idx=1))
        response = DELETE(url, headers)

    response = response.json()
    return response


################################################################################
# WEBHOOK
################################################################################


@csrf_exempt
def receive_github_hook(request):
    """receive_hook will receive a Github webhook, generate a new Container
     for the collection, and then send the image to the build queue. For now,
     we accept just collection builds

    :: notes
    - The container collection (repo) is looked up via the repo's Github name
    - The user must be the owner of the container collection, associated with
      the Github account
    """
    # We do these checks again for sanity
    if request.method == "POST":

        if DISABLE_GITHUB or DISABLE_BUILDING:
            return JsonResponseMessage(message="Building is disabled")

        if not re.search("GitHub-Hookshot", request.META["HTTP_USER_AGENT"]):
            return JsonResponseMessage(message="Agent not allowed")

        # Only allow application/json content type
        if request.META["CONTENT_TYPE"] != "application/json":
            return JsonResponseMessage(message="Incorrect content type")

        # Check that it's coming from the right place
        required_headers = ["HTTP_X_GITHUB_DELIVERY", "HTTP_X_GITHUB_EVENT"]
        if not check_headers(request, required_headers):
            return JsonResponseMessage(message="Agent not allowed")

        # Has to be a ping or push
        if request.META["HTTP_X_GITHUB_EVENT"] not in ["ping", "push", "deployment"]:
            return JsonResponseMessage(message="Incorrect delivery method.")

        # Parse the body
        payload = load_body(request)
        repo = payload.get("repository")

        print(repo["full_name"])
        try:
            collection = Collection.objects.get(name=repo["full_name"])
        except Collection.DoesNotExist:
            return JsonResponseMessage(message="Collection not found", status=404)

        # Update repo metadata that might change
        collection.metadata["github"].update(update_webhook_metadata(repo))
        collection.save()

        # We only currently parse user collections for Github
        do_build = False

        # We build on deployment
        if "deployment" in payload:
            if payload["deployment"]["task"] == "deploy":
                do_build = True

        else:
            do_build = True

        print("IN RECEIVE HOOK, DO BUILD IS %s" % do_build)
        if do_build:
            return verify_payload(request, collection)

        return JsonResponseMessage(
            status_message="Received, building disabled.", status=200
        )
    return JsonResponseMessage(message="Invalid request.")


def verify_payload(request, collection):
    """verify payload will verify a payload"""

    from shub.plugins.google_build.tasks import parse_hook
    from shub.plugins.google_build.actions import is_over_limit

    payload = load_body(request)

    # Validate the payload with the collection secret
    signature = request.META.get("HTTP_X_HUB_SIGNATURE")
    if not signature:
        return JsonResponseMessage(message="Missing credentials.")

    status = validate_payload(
        collection=collection, payload=request.body, request_signature=signature
    )
    if not status:
        return JsonResponseMessage(message="Invalid credentials.")

    # If a branch is provided, this is the version  "ref": "refs/heads/master",
    try:
        branch = payload.get("ref", "refs/heads/master").replace("refs/heads/", "")
    except:
        branch = "master"

    # Some newer webhooks have commits
    commits = payload.get("commits")

    # Ensure we aren't over limit
    if is_over_limit():
        message = (
            "Registry concurrent build limit is "
            + "%s" % SREGISTRY_GOOGLE_BUILD_LIMIT
            + ". Please try again later."
        )

        return JsonResponseMessage(message=message, status_message="Permission Denied")

    django_rq.enqueue(parse_hook, cid=collection.id, branch=branch, commits=commits)

    return JsonResponseMessage(
        message="Hook received and parsing.", status=200, status_message="Received"
    )
