"""

Copyright (C) 2017-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from rest_framework.permissions import DjangoObjectPermissions, SAFE_METHODS

from shub.logger import bot
from shub.apps.users.models import User
from shub.settings import USER_COLLECTIONS

import base64
import hashlib
import hmac
import re


def _parse_header(auth):
    """parse a header and check for the correct digest.

       Parameters
       ==========
       auth: the challenge from the header      
    """

    header, content = auth.split(" ")
    content = content.split(",")
    values = dict()
    for entry in content:
        key, val = re.split("=", entry, 1)
        values[key] = val

    values["header"] = header
    return values


def get_request_user(auth, user=None):
    """get the user for the request from an authorization object
     
       Parameters
       ==========
       auth: the authentication object
       user: will return as None if not able to obtain from auth

    """
    values = _parse_header(auth)

    if "Credential" not in values:
        bot.debug("Headers missing, request is invalid.")
        return user

    _, username, _ = values["Credential"].split("/")
    username = base64.b64decode(username).decode("utf-8")

    try:
        user = User.objects.get(username=username)
    except:
        bot.debug("%s is not a valid user, request invalid." % username)
    return user


def has_push_permission(user, collection=None):
    """determine if the user has pull permission. This coincides with being
       an owner of a collection, or a global admin or superuser.
     
       Parameters
       ==========
       user: the user to check
       collection: the collection to check for

    """

    if user.is_superuser or user.is_staff:
        return True

    # A new collection is pushable for a regular user if USER_COLLECTIONS True
    if collection is None:
        return USER_COLLECTIONS

    # Otherwise, only owners can push to an existing
    if user in collection.owners.all():
        return True

    return False


def has_pull_permission(user, collection=None):
    """a simple function to parse an authentication challenge for the username,
       and determine if the user has permission to perform the action.
       The instance in question is a collection
     
       Parameters
       ==========
       auth: the challenge from the header
       instance: the instance to check for
       permission: the permission needed
       pull_permission: if True, the user is asking to pull. If False, push

    """
    if user.is_superuser or user.is_staff:
        return True

    # The collection must exist!

    if collection is not None:

        return collection.has_view_permission(user)

    return False


def has_permission(auth, collection=None, pull_permission=True):
    """a simple function to parse an authentication challenge for the username,
       and determine if the user has permission to perform the action.
       The instance in question is a collection
     
       Parameters
       ==========
       auth: the challenge from the header
       collection: the collection instance to check for
       pull_permission: if True, the user is asking to pull. If False, push

    """
    user = get_request_user(auth)
    if user is None:
        return False

    if pull_permission is True:
        return has_pull_permission(user, collection)
    return has_push_permission(user, collection)


def validate_request(auth, payload, sender="push", timestamp=None, superuser=True):

    """validate header and payload for a request

    Parameters
    ==========
    auth: the Authorization header content
    payload: the payload to assess
    timestamp: the timestamp associated with the request
    superuser: if the user must be superuser for validity

    Returns
    =======
    True if the request is valid, False if not

    """
    values = _parse_header(auth)

    if values["header"] != "SREGISTRY-HMAC-SHA256":
        print("Invalid SREGISTRY Authentication scheme, request invalid.")
        return False

    if "Credential" not in values or "Signature" not in values:
        print("Headers missing, request is invalid.")
        return False

    kind, username, ts = values["Credential"].split("/")
    username = base64.b64decode(username).decode("utf-8")
    if kind != sender:
        print("Mismatch: type (%s) sender (%s) invalid." % (kind, sender))
        return False

    if timestamp is not None:
        if ts != timestamp:
            bot.debug("%s is expired, must be %s." % (ts, timestamp))
            return False

    try:
        user = User.objects.get(username=username)
    except:
        print("%s is not a valid user, request invalid." % username)
        return False

    request_signature = values["Signature"]
    secret = user.token
    return validate_secret(secret, payload, request_signature)


def encode(item):
    """ encode an item to bytes to work with hexdigest

    Parameters
    ==========
    item: some string or bytes value to check
    """
    if not isinstance(item, bytes):
        item = item.encode("utf-8")
    return item


def validate_secret(secret, payload, request_signature):
    """ use hmac digest to compare a request_signature to one generated
    using a server secret against a payload. Valid means matching.

    Parameters
    ==========
    secret: the secret to generate the hash
    payload: the content to include in the digest
    request_signature: the signature generated by the request
                       to check against

    Returns
    =======
    True if secret + payload to generate signature matches 
                       request signature

    """
    payload = encode(payload)
    request_signature = encode(request_signature)
    secret = encode(secret)
    digest = (
        hmac.new(secret, digestmod=hashlib.sha256, msg=payload)
        .hexdigest()
        .encode("utf-8")
    )
    return hmac.compare_digest(digest, request_signature)


################################################################################
# PERMISSIONS
################################################################################


class ObjectOnlyPermissions(DjangoObjectPermissions):
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user
            and request.user.is_authenticated
        )
