"""

Copyright (C) 2017-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.http import JsonResponse
from .actions import get_endpoints, do_transfer, search_endpoints
from .decorators import has_globus_association
from shub.apps.main.views import get_container
from shub.plugins.globus.utils import get_client, get_transfer_client, associate_user

from shub.settings import VIEW_RATE_LIMIT as rl_rate, VIEW_RATE_LIMIT_BLOCK as rl_block

from ratelimit.decorators import ratelimit
from social_django.models import UserSocialAuth
from globus_sdk.exc import TransferAPIError


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
@login_required
@has_globus_association
def globus_logout(request):
    """log the user out of globus - this is a complete disconnect meaning
    that we revoke tokens and delete the social auth object.
    """
    client = get_client()

    try:

        # Properly revoke and log out
        social = request.user.social_auth.get(provider="globus")
        for _, token_info in social.extra_data.items():
            for token, token_type in token_info.items():
                client.oauth2_revoke_token(
                    token, additional_params={"token_type_hint": token_type}
                )

        social.delete()

    except UserSocialAuth.DoesNotExist:
        pass

    # Redirect to globus logout page?
    redirect_name = "Singularity Registry"
    redirect_url = "%s%s" % (settings.DOMAIN_NAME, reverse("profile"))
    logout_url = "https://auth.globus.org/v2/web/logout"
    params = "?client=%s&redirect_uri=%s&redirect_name=%s" % (
        client.client_id,
        redirect_url,
        redirect_name,
    )
    return redirect("%s%s" % (logout_url, params))


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
@login_required
def globus_login(request):
    """
    Associate the logged in user with a globus account based on email.
    If the association doesn't exist, create it. Redirect to transfer
    page.
    """

    redirect_uri = reverse("globus_login")
    # http://localhost/globus/login/"

    client = get_client()
    client.oauth2_start_flow(redirect_uri, refresh_tokens=True)

    # First step of authentication flow - we need code
    if "code" not in request.GET:
        auth_uri = client.oauth2_get_authorize_url()
        return redirect(auth_uri)

    else:

        # Second step of authentication flow - we need to ask for token
        code = request.GET.get("code")
        associate_user(request.user, client=client, code=code)

    return redirect("globus_transfer")


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
@login_required
@has_globus_association
def globus_transfer(request, cid=None, endpoints=None):
    """a main portal for working with globus. If the user has navigated
    here with a container id, it is presented with option to do a
    transfer. If the method is a POST, we also do a custom search
    for a set of containers.
    """
    container = None
    if cid is not None:
        container = get_container(cid)

    context = {
        "user": request.user,
        "container": container,
        "endpoint_search_term": "Search for...",
    }

    # Does the user want to search endpoints?

    if request.method == "POST":
        term = request.POST.get("term")
        if term is not None:
            endpoints = search_endpoints(term=term, user=request.user)
            context["endpoint_search_term"] = term.capitalize()

    # If we don't have any endpoints still

    if endpoints is None:
        endpoints = get_endpoints(request.user)

    context["endpoints"] = endpoints

    return render(request, "globus/transfer.html", context)


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
@login_required
@has_globus_association
def globus_endpoint(request, endpoint_id=None, cid=None):
    """Show information for a single endpoint only."""
    container = None
    if cid is not None:
        container = get_container(cid)

    context = {
        "user": request.user,
        "container": container,
        "endpoint_search_term": "Search for...",
    }

    # Get the endpoint
    try:
        client = get_transfer_client(request.user)
        endpoints = [client.get_endpoint(endpoint_id).data]
    except TransferAPIError:
        endpoints = get_endpoints(request.user)

    context["endpoints"] = endpoints

    return render(request, "globus/transfer.html", context)


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
@login_required
@has_globus_association
def submit_transfer(request, endpoint, cid):
    """submit a transfer request for a container id to an endpoint, also
    based on id
    """

    container = get_container(cid)
    if container is None:
        m = "This container could not be found."

    else:
        result = do_transfer(user=request.user, endpoint=endpoint, container=container)

        link = "https://globus.org/app/activity/%s" % result["task_id"]
        m = result["message"]
        m = "%s: <a target='_blank' href='%s'>view task</a>" % (m, link)

    status = {"message": m}
    return JsonResponse(status)
