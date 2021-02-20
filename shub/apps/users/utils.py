"""

Copyright (C) 2017-2021 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from rest_framework.authtoken.models import Token
import hashlib
import base64
import sys
import os


def get_user(uid):
    """get a user based on id

    Parameters
    ==========
    uid: the id of the user
    """
    from shub.apps.users.models import User

    keyargs = {"id": uid}
    try:
        user = User.objects.get(**keyargs)
    except User.DoesNotExist:
        user = None
    else:
        return user


def get_usertoken(user):
    try:
        token = Token.objects.get(user=user)
    except Token.DoesNotExist:
        token = Token.objects.create(user=user)
    return token.key


def create_code_challenge():
    """This function will produce a verifier and challenge for Native Application
    flow with OAuth2. We always use SHA256 and the code verifier is between 43
    and 128 in length.

    verifier: an unhashed secret
    challenge: a base64 encoded (hashed) version, sent at the start
        Must only contain the following characters: [a-zA-Z0-9~_.-].

    derived from https://github.com/globus/globus-sdk-python/blob/master/globus_sdk/auth/oauth2_native_app.py
    """
    code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode("utf-8").rstrip("=")

    hashed_verifier = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    # urlsafe base64 encode that hash and strip the padding
    code_challenge = (
        base64.urlsafe_b64encode(hashed_verifier).decode("utf-8").rstrip("=")
    )

    # return the verifier and the encoded hash
    return code_verifier, code_challenge


################################################################################
# HEADERS
################################################################################


def basic_auth_header(username, password):
    """return a base64 encoded header object to
    generate a token

    Parameters
    ==========
    username: the username
    password: the password
    """
    s = "%s:%s" % (username, password)
    if sys.version_info[0] >= 3:
        s = bytes(s, "utf-8")
        credentials = base64.b64encode(s).decode("utf-8")
    else:
        credentials = base64.b64encode(s)
    auth = {"Authorization": "Basic %s" % credentials}
    return auth
