"""

Copyright (C) 2017-2021 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from shub.apps.main.models import Container, Label
from shub.apps.library.views.minio import delete_minio_container

from shub.settings import VIEW_RATE_LIMIT as rl_rate, VIEW_RATE_LIMIT_BLOCK as rl_block

from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.contrib import messages
from datetime import datetime
from ratelimit.decorators import ratelimit


# get container
def get_container(cid):
    keyargs = {"id": cid}
    try:
        container = Container.objects.get(**keyargs)
    except Container.DoesNotExist:
        raise Http404
    else:
        return container


################################################################################
# HELPERS ######################################################################
################################################################################


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def view_container(request, cid):
    container = get_container(cid)

    if not container.has_view_permission(request):
        messages.info(request, "This container is private.")
        return redirect("collections")

    messages.info(request, "We don't know what to do for this view yet, ideas?")
    return redirect("collection_details", cid=container.collection.id)


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def view_named_container(request, collection, name, tag):
    """view a specific container based on a collection, container, and tag"""
    try:
        container = Container.objects.get(
            collection__name=collection, name=name, tag=tag
        )
    except Container.DoesNotExist:
        messages.info(request, "Container not found.")
        return redirect("collections")

    return container_details(request, container.id)


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def container_details(request, cid):
    container = get_container(cid)

    if not container.has_view_permission(request):
        messages.info(request, "This container is private.")
        return redirect("collections")

    edit_permission = container.has_edit_permission(request)
    labels = Label.objects.filter(containers=container)
    context = {
        "container": container,
        "labels": labels,
        "edit_permission": edit_permission,
    }
    return render(request, "containers/container_details.html", context)


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
@login_required
def save_container_description(request, cid):
    """allow an owner of a collection to change the descriptions
    via a contenteditable field
    """
    container = get_container(cid=cid)
    if not container.has_edit_permission(request):
        return JsonResponse({"result": "This action is not permitted."})

    if request.method == "POST":
        description = request.POST.get("description")
        if description:
            container.metadata["description"] = description
            container.save()
            return JsonResponse({"result": "Description updated"})
    return JsonResponse({"result": "Nope, can't do that"})


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
@login_required
def delete_container(request, cid):
    """delete a container, including it's corresponding files"""
    container = get_container(cid)

    if not container.has_edit_permission(request):
        messages.info(request, "This action is not permitted.")
        return redirect("collections")

    delete_minio_container(container)
    container.delete()
    messages.info(request, "Container successfully deleted.")
    return redirect(container.collection.get_absolute_url())


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def container_tags(request, cid):
    """view container tags"""
    container = get_container(cid)

    if not container.has_view_permission(request):
        messages.info(request, "This container is private.")
        return redirect("collections")

    context = {"container": container}
    return render(request, "containers/container_tags.html", context)


################################################################################
# FREEZE #######################################################################
################################################################################


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
@login_required
def change_freeze_status(request, cid):
    """freeze or unfreeze a container

    Parameters
    ==========
    cid: the container to freeze or unfreeze
    """
    container = get_container(cid)
    edit_permission = container.has_edit_permission(request)

    if edit_permission:

        # If the container wasn't frozen, assign new version
        # '2017-08-06T19:28:43.294175'
        if container.version is None and container.frozen is False:
            container.version = datetime.now().isoformat()

        container.frozen = not container.frozen
        container.save()
        message = "Container %s:%s be overwritten by new pushes." % (
            container.name,
            container.tag,
        )
        if container.frozen:
            message = "%s:%s is frozen, and will not be overwritten by push." % (
                container.name,
                container.tag,
            )

        messages.info(request, message)
    else:
        messages.info(request, "You do not have permissions to perform this operation.")

    previous_page = request.META.get("HTTP_REFERER", None)
    if previous_page is not None:
        return HttpResponseRedirect(previous_page)

    return redirect("container_details", cid=container.id)
