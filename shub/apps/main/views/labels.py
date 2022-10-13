"""

Copyright (C) 2017-2022 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.contrib import messages
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.http.response import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from ratelimit.decorators import ratelimit

from shub.apps.main.models import Label
from shub.settings import VIEW_RATE_LIMIT as rl_rate
from shub.settings import VIEW_RATE_LIMIT_BLOCK as rl_block

#### GETS #############################################################


def get_label(key=None, value=None):

    keyargs = {}
    if key is not None:
        keyargs["key"] = key
    if value is not None:
        keyargs["value"] = value

    try:
        label = Label.objects.get(**keyargs)
    except Label.DoesNotExist:
        raise Http404
    else:
        return label


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def all_labels(request):
    # Generate queryset of labels annotated with count based on key, eg {'key': 'maintainer', 'id__count': 1}
    labels = Label.objects.values("key").annotate(Count("id")).order_by()
    context = {"labels": labels}
    return render(request, "labels/all_labels.html", context)


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def view_label(request, lid):
    """view containers with a specific, exact key/pair"""
    try:
        label = Label.objects.get(id=lid)
    except:
        messages.info(request, "This label does not exist.")
        return redirect("all_labels")

    context = {"label": label}

    return render(request, "labels/view_label.html", context)


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def view_label_keyval(request, key, value):
    """view containers with a specific, exact key/pair"""
    try:
        label = Label.objects.get(key=key, value=value)
    except:
        messages.info(request, "This label does not exist.")
        return redirect("all_labels")

    url = reverse("view_label_id", kwargs={"lid": label.id})
    return HttpResponseRedirect(url)


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def view_label_key(request, key):
    """view all labels with a shared key"""
    labels = Label.objects.filter(key=key)
    context = {"labels": labels, "key": key}
    return render(request, "labels/view_label_key.html", context)


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def update_container_labels(container, labels):
    for name, value in labels.items():
        if isinstance(value, str):
            value = value.lower()

        label, _ = Label.objects.get_or_create(key=name.lower(), value=value)

        label.save()

        # Does the container have the label with a different value?
        oldies = Label.objects.filter(
            Q(containers=container) & Q(key=name.lower)
        ).exclude(value=value)

        for oldie in oldies:
            oldie.containers.remove(container)
            oldie.save()

        if container not in label.containers.all():
            label.containers.add(container)
        container.save()
    return container
