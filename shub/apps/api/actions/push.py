"""

Copyright 2017-2023 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""


import json
import uuid

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ratelimit.decorators import ratelimit
from rest_framework.exceptions import PermissionDenied

from shub.apps.api.utils import get_request_user, has_permission, validate_request
from shub.apps.main.models import Collection
from shub.apps.main.utils import format_collection_name
from shub.settings import DISABLE_BUILDING
from shub.settings import VIEW_RATE_LIMIT as rl_rate
from shub.settings import VIEW_RATE_LIMIT_BLOCK as rl_block
from sregistry.main.registry.auth import generate_timestamp


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
@csrf_exempt
def collection_auth_check(request):
    """check permissions and
    return a collection id (cid) if a collection exists and the user
    has permission to upload. If not, a permission denied is returned.
    """
    if DISABLE_BUILDING:
        raise PermissionDenied(detail="Push is disabled.")

    auth = request.META.get("HTTP_AUTHORIZATION", None)

    # Load the body, which is json with variables
    body_unicode = request.body.decode("utf-8")
    body = json.loads(body_unicode)

    # Get variables
    tag = body.get("tag", "latest")
    name = body.get("name")
    collection_name = format_collection_name(body.get("collection"))

    print(tag, name, collection_name, auth, body)

    # Authentication always required for push
    if auth is None:
        raise PermissionDenied(detail="Authentication Required")

    owner = get_request_user(auth)
    timestamp = generate_timestamp()
    payload = "push|%s|%s|%s|%s|" % (collection_name, timestamp, name, tag)

    # Validate Payload
    if not validate_request(auth, payload, "push", timestamp):
        raise PermissionDenied(detail="Unauthorized")

    try:
        collection = Collection.objects.get(name=collection_name)

    except Collection.DoesNotExist:
        collection = None

    # Validate User Permissions, either for creating collection or adding
    # Here we have permission if:
    # 1- user collections are enabled with USER_COLLECTIONS
    # 2- the user is a superuser or staff
    # 3- the user is owner of a collection
    if not has_permission(auth, collection, pull_permission=False):
        raise PermissionDenied(detail="Unauthorized")

    # If the user cannot create a new collection
    if not owner.has_create_permission():
        raise PermissionDenied(detail="Unauthorized")

    # If we get here user has create permission, does collection exist?
    if collection is None:
        collection = Collection.objects.create(
            name=collection_name, secret=str(uuid.uuid4())
        )
        collection.save()
        collection.owners.add(owner)
        collection.save()

    # Return json response with collection id
    return JsonResponse({"cid": collection.id})
