"""

Copyright (C) 2017-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from shub.apps.users.models import User
from shub.apps.main.models import Collection, Star
from shub.apps.logs.models import APIRequestCount
from shub.settings import VIEW_RATE_LIMIT as rl_rate, VIEW_RATE_LIMIT_BLOCK as rl_block

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q, Sum
from ratelimit.decorators import ratelimit
from rest_framework.authtoken.models import Token


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
@login_required
def view_token(request):
    """ tokens are valid for pushing (creating collections) and only available
        to superusers or staff, unless USER_COLLECTIONS is set to True. If
        user's are allowed to create collections, they can push to those for
        which they are an owner or contributor. 
    """
    return render(request, "users/token.html")


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
@login_required
def update_token(request):
    """a user is allowed to change/update their current token
    """
    try:
        token = Token.objects.get(user=request.user)
        token.delete()
    except Token.DoesNotExist:
        pass

    token = Token.objects.create(user=request.user)
    token.save()

    return render(request, "users/token.html")


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def view_profile(request, username=None):
    """view a user's profile, including collections and download counts
    """

    message = "You must select a user or be logged in to view a profile."
    if not username:
        if not request.user:
            messages.info(request, message)
            return redirect("collections")
        user = request.user
    else:
        user = get_object_or_404(User, username=username)

    if user == request.user:
        collections = (
            Collection.objects.filter(owners=user)
            .annotate(Count("star", distinct=True))
            .order_by("-star__count")
        )
    else:
        collections = (
            Collection.objects.filter(owners=user, private=False)
            .annotate(Count("star", distinct=True))
            .order_by("-star__count")
        )

    # Total Starred Collections

    stars = Star.objects.filter(collection__owners=user).count()
    favorites = Star.objects.filter(user=user)

    # Total Downloads Across Collections

    downloads = APIRequestCount.objects.filter(
        Q(method="get", path__contains="ContainerDetailByName", collection__owners=user)
        | Q(
            method="get", path__contains="ContainerBasicByName", collection__owners=user
        )
    ).aggregate(Sum("count"))

    downloads = downloads["count__sum"]

    context = {
        "profile": user,
        "collections": collections,
        "downloads": downloads,
        "stars": stars,
        "favorites": favorites,
    }

    return render(request, "users/profile.html", context)


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
@login_required
def delete_account(request):
    """delete a user's account and all associated containers."""
    from shub.settings import PLUGINS_ENABLED

    from shub.apps.main.views.collections import _delete_collection

    if "google_build" in PLUGINS_ENABLED:
        from shub.plugins.google_build.views import _delete_collection

    if not request.user or request.user.is_anonymous:
        messages.info(request, "This action is not prohibited.")
        return redirect("index")

    # Delete collections first
    collections = Collection.objects.filter(owners=request.user)

    # Delete each collection
    for collection in collections:
        _delete_collection(request, collection)

    # Log the user out
    logout(request)
    request.user.is_active = False
    messages.info(request, "Thank you for using Singularity Registry Server!")
    return redirect("index")
