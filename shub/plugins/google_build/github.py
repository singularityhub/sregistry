'''

Copyright (C) 2016-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

import json
import requests

from django.http import (
    HttpResponse, 
    JsonResponse
)

from django.urls import reverse
from shub.apps.users.models import User
from shub.logger import bot

from django.views.decorators.csrf import csrf_exempt

from rest_framework import (
    authentication, 
    status
)

from rest_framework.response import Response

from shub.apps.main.models import (
    Container, 
    Collection
)

from .utils import (
    check_headers,
    format_params,
    get_default_headers,
    JsonResponseMessage, 
    load_body,
    paginate,
    validate_payload
)

from .utils import (
    DELETE,
    POST
)

from shub.settings import DOMAIN_NAME

from dateutil.parser import parse
import json
import os
from datetime import datetime
import pickle
import re
import requests
import uuid


api_base = 'https://api.github.com'


## Calls

def get_auth(user, headers=None, idx=0):
    '''get_auth will return the authentication header for a user
       the default headers (without auth) are returned if provider not github

       Parameters
       ==========
       user: a user object
    '''
    if headers is None:
        headers = get_default_headers()
    token = get_auth_token(user, idx)
    if token is not None:
        token = "token %s" %(token)
        headers["Authorization"] = token
    return headers


def get_auth_token(user, idx=0):
    '''get_auth_token will return the auth token for a user.

       Parameters
       ==========
       user: a user object
    '''
    # 1. Github private first priority
    auth = [x for x in user.social_auth.all() if x.provider == 'github-private']

    # 2. Github public second priority
    if len(auth) == 0:
        auth = [x for x in user.social_auth.all() if x.provider == 'github']

    if len(auth) > idx:
        return auth[idx].access_token
    else:
        return auth[0].access_token


def get_repo(user, reponame, username, headers=None):
    '''get_repo will return a single repo, username/reponame
       given authentication with user

       Parameters
       ==========
       user: the user to get github credentials for
       reponame: the name of the repo to retrieve
       username: the username of the repo (owner)
    '''
    # Case 1, the user just has one auth or just public
    if headers is None:
        headers = get_auth(user)
    headers['Accept'] = "application/vnd.github.mercy-preview+json" 
    url = "%s/repos/%s/%s" %(api_base,username,reponame)
    response = requests.get(url,headers=headers)

    # Case 2: public and private
    if response.status_code != 200:
        auth_headers = get_auth(user, idx=1)
        headers.update(auth_headers)
        response = requests.get(url, headers=headers)
    response = response.json()
    return response


def list_repos(user, headers=None):
    '''list_repos will list the public repos for a user

       Parameters
       ==========
       user: a user object to list
       headers: headers to replace default
    '''
    if headers is None:
        headers = get_auth(user)
    url = "%s/user/repos" %(api_base)
    repos = paginate(url=url,headers=headers)

    if not repos:
        auth_headers = get_auth(user, idx=1)
        headers.update(auth_headers)
        repos = paginate(url=url,headers=headers)
    return repos


def get_commits(user, uri, headers=None, sha=None, limit=None):
    '''list_repos will list the public repos for a user

       Parameters
       ==========
       user: the user that owns the repository
       uri: the username/repo
       page: the page of results to return, if none, paginates
    '''
    if not headers:
        headers = get_auth(user)
    headers['Accept'] = "application/vnd.github.cryptographer-preview"
    url = "%s/repos/%s/commits" %(api_base, uri)

    # Option 1: return a sha
    if sha:
        url = "%s/%s" %(url, sha)
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            headers.update(get_auth(user, idx=1))
            response = requests.get(url, headers=headers)
        return [response.json()]

    # Option 2, return paginated commits
    commits = paginate(url=url, headers=headers, limit=limit)
    if len(commits) == 0:
        auth_headers = get_auth(user, idx=1)
        headers.update(auth_headers)
        commits = paginate(url=url,headers=headers,limit=limit)
    bot.debug('Found %s commits'%len(commits))
    return commits


def get_branch_commits(user, uri, branch):
    '''get all commits for a particular branch
    '''
    headers = get_auth(user)
    headers['Accept'] = "application/vnd.github.cryptographer-preview"
    url = "%s/repos/%s/commits?sha=%s" %(api_base, uri, branch)
    response = requests.get(url=url, headers=headers)
    if response.status_code != 200:
        auth_headers = get_auth(user, idx=1)
        headers.update(auth_headers)
        response = requests.get(url=url,headers=headers)
    return response.json()


def get_commit_date(commit):
    '''return the commit author date, then the committer'''
    return (commit['commit'].get('author').get('date') or 
            commit['commit'].get('committer').get('date'))


def get_commits_since(commits, since):
    '''from a list of commits, return those in a list that occured since
       a provided date (since)
    '''
    updates = []
    seen = []

    def isnew(changed,since):
        if isinstance(since, int):
            since = datetime.fromtimestamp(since).strftime('%Y-%m-%dT%H:%M:%SZ')
        if parse(changed) >= parse(since):
            return True
        return False

    for commit in commits:
        commit_date = get_commit_date(commit)
        if isnew(commit_date,since) and commit['sha'] not in seen:
            updates.append(commit)
            seen.append(commit['sha'])

    return updates


def get_commit_details(collection, since=None, headers=None, limit=None):
    '''get changed files will find changed files since a particular date.
       If since is not defined, we take the following logic:
        
       1. First compare the commits date against the repo pushed_date. If 
          commits are found, differences are determined between those ranges.
       2. If the webhook was created without a new commit/push, then fall back
          to comparing commits to the webhook creation date
       3. If still no passing ranges, parse entire result for changed files,
          and return the most recent of each.
    '''
    if since is None:
        since = collection.metadata['github']['pushed_at']
    commits = get_commits(user=collection.owners.first(), # user created repo 
                          uri=collection.metadata['github']['repo_name'],
                          limit=limit)

    # If the collection has no containers, assess all commits
    if not collection.containers.count():
        updates = commits
    else:
        # First pass, commit date vs. repo[pushed_at]
        updates = get_commits_since(commits, since)
   
    # Second pass, commit date vs. webhook[created_at]
    if not updates:
        since = collection.metadata['webhook']['created_at']
        updates = get_commits_since(commits, since)

    # Last try, since repo created
    if not updates:
        since = collection.metadata['github']['created_at']
        updates = get_commits_since(commits, since)

    commits = []

    # Retrieve commits with complete list of changes
    for commit in updates:
        response = get_commits(user=collection.owners.first(),
                               uri=collection.metadata['github']['repo_name'], 
                               sha=commit['sha'])
        if response:
            commits = commits + response
    return commits


## Create

def create_webhook(user, repo, secret):
    '''create_webhook will create a webhook for a repo to send back
       to singularity hub on push

       Parameters
       ==========
       user: user: should be a singularity hub user. This is used to get
                   the Github authentication
       repo: should be a complete repo object, including username and reponame
       secret: should be a randomly generated string, created when repo connected,
               to validate future pushes
    '''
    headers = get_auth(user)
 
    url = "%s/repos/%s/hooks" %(api_base, repo['full_name'])

    callback_url = "%s/%s" %(DOMAIN_NAME, reverse('receive_hook'))

    config = { "url": callback_url,
               "content_type": "json",
               "secret": secret }

    params = { "name" : "web",
               "active" : True,
               "events" : ["push", "deployment"],
               "config" : config }

    # Create webhook
    response = POST(url, headers=headers, data=params)
    if response.status_code is not 201:
        headers.update(get_auth(user, idx=1))
        response = POST(url, headers=headers, data=params)

    response = response.json()

    # Get topics
    full_repo = get_repo(user=user,
                         headers=headers,
                         reponame=repo['name'],
                         username=repo['owner']['login'])

    response['topics'] = full_repo['topics']
    return response


## Delete

def delete_webhook(user, repo):
    '''delete_webhook will delete a webhook, done when a user deletes a collection.

       Parameters
       ==========
       user: should be a singularity hub user. This is used to get
             the Github authentication
       repo: should be a complete repo object, including username and reponame
       secret: should be the randomly generated string created when repo was connected.
    '''
    headers = get_auth(user)

    url = "%s/repos/%s/%s/hooks/%s" %(api_base,
                                      repo['owner']['login'],
                                      repo['name'],
                                      repo['id'])
 
    response = DELETE(url,headers)
    if response.status_code != 200:
        headers.update(get_auth(user, idx=1))
        response = DELETE(url,headers)

    response = response.json()
    return response




################################################################################
# WEBHOOK
################################################################################


@csrf_exempt
def receive_github_hook(request):
    '''receive_hook will receive a Github webhook, generate a new Container 
       for the collection, and then send the image to the build queue. For now,
       we accept just collection builds

      :: notes
      - The container collection (repo) is looked up via the repo's Github name
      - The user must be the owner of the container collection, associated with 
        the Github account
    '''

    # We do these checks again for sanity
    if request.method == "POST":

        # Has to have Github-Hookshot
        if not re.search('GitHub-Hookshot',request.META["HTTP_USER_AGENT"]):
            return JsonResponseMessage(message="Agent not allowed")

        # Only allow application/json content type
        if request.META["CONTENT_TYPE"] != "application/json":
            return JsonResponseMessage(message="Incorrect content type")
        
        # Check that it's coming from the right place
        required_headers = ['HTTP_X_GITHUB_DELIVERY', 'HTTP_X_GITHUB_EVENT']
        if not check_headers(request, required_headers):
            return JsonResponseMessage(message="Agent not allowed")

        # Has to be a ping or push
        if request.META["HTTP_X_GITHUB_EVENT"] not in ["ping", "push", "deployment"]:
            return JsonResponseMessage(message="Incorrect delivery method.")

        # Parse the body
        payload = load_body(request)
        repo = payload.get('repository')

        try:
            collection = Collection.objects.get(name=repo['full_name'])
        except Collection.DoesNotExist:
            return JsonResponseMessage(message="Collection not found",
                                       status=404)

        # We only currently parse user collections for Github
        do_build = False

        # We build on deployment
        if "deployment" in payload:
            if payload['deployment']['task'] == "deploy":
                do_build = True

        else:
            do_build = True

        print("IN RECEIVE HOOK, DO BUILD IS %s" % do_build)
        if do_build:
            return verify_payload(request, collection)

        return JsonResponseMessage(status_message="Received, building disabled.", status=200)
    return JsonResponseMessage(message="Invalid request.")


def verify_payload(request, collection):
    '''verify payload will verify a payload'''

    from shub.plugins.google_build.tasks import parse_hook

    payload = load_body(request)
    repo = payload.get('repository')

    # Validate the payload with the collection secret
    signature = request.META.get('HTTP_X_HUB_SIGNATURE')
    if not signature:
        return JsonResponseMessage(message="Missing credentials.")

    status = validate_payload(collection=collection, 
                              payload=request.body, 
                              request_signature=signature)
    if not status:
        return JsonResponseMessage(message="Invalid credentials.")

    # If a branch is provided, this is the version  "ref": "refs/heads/master",
    try:
        branch = payload.get('ref','refs/heads/master').replace('refs/heads/','')
    except:
        branch = "master"

    # Some newer webhooks have commits
    commits = payload.get('commits')
    res = parse_hook(cid=collection.id,
                     branch=branch,
                     commits=commits)

    print(res)
    return JsonResponseMessage(message="Hook received and parsing.",
                               status=200,
                               status_message="Received") 
