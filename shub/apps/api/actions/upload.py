"""

Copyright (C) 2017-2022 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

import os

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from ratelimit.decorators import ratelimit
from rest_framework.exceptions import PermissionDenied

from shub.apps.api.utils import get_request_user, has_permission, validate_request
from shub.apps.main.models import Collection
from shub.settings import DISABLE_BUILDING
from shub.settings import VIEW_RATE_LIMIT as rl_rate
from shub.settings import VIEW_RATE_LIMIT_BLOCK as rl_block
from sregistry.main.registry.auth import generate_timestamp

# Terminal Upload


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
@csrf_exempt
def upload_complete(request):
    """view called on /api/upload/complete after nginx upload module finishes."""
    from shub.apps.api.actions.create import upload_container

    if request.method == "POST":

        path = request.POST.get("file1.path")
        size = request.POST.get("file1.size")
        cid = request.POST.get("collection")
        filename = request.POST.get("file1.name")
        name = request.POST.get("name")
        version = request.POST.get("file1.md5")
        auth = request.META.get("HTTP_AUTHORIZATION", None)
        tag = request.POST.get("tag")
        csrftoken = request.META.get("CSRF_COOKIE")

        if auth is None and csrftoken is None:
            if os.path.exists(filename):
                os.remove(path)
            raise PermissionDenied(detail="Authentication Required")

        if DISABLE_BUILDING:
            if os.path.exists(filename):
                os.remove(path)
            raise PermissionDenied(detail="Uploading is disabled.")

        # at this point, the collection MUST exist
        try:
            collection = Collection.objects.get(id=cid)
        except Collection.DoesNotExist:
            raise PermissionDenied(detail="Authentication Required")

        # If not defined, coming from terminal
        web_interface = True
        if csrftoken is None:
            web_interface = False
            owner = get_request_user(auth)
            timestamp = generate_timestamp()
            payload = "upload|%s|%s|%s|%s|" % (collection.name, timestamp, name, tag)

            # Validate Payload
            if not validate_request(auth, payload, "upload", timestamp):
                raise PermissionDenied(detail="Unauthorized")

            if not has_permission(auth, collection, pull_permission=False):
                raise PermissionDenied(detail="Unauthorized")

        else:
            owner = request.user

        # If tag is provided, add to name
        if tag is not None:
            name = "%s:%s" % (name, tag)

        # Expected params are upload_id, name, md5, and cid
        message = upload_container(
            cid=collection.id,
            user=owner,
            version=version,
            upload_id=path,
            name=name,
            size=size,
        )

        # If the function doesn't return a message (None), indicates success
        if message is None:
            message = "Upload Complete"

        if web_interface is True:
            messages.info(request, message)
            return redirect(collection.get_absolute_url())
        return JsonResponse({"message": message})

    return redirect("collections")


class UploadUI(LoginRequiredMixin, TemplateView):
    template_name = "routes/upload.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["collection"] = Collection.objects.get(id=context["cid"])
        return context
