"""

Copyright (c) 2017-2020, Vanessa Sochat, All rights reserved.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.conf import settings
from social_django.models import UserSocialAuth
import globus_sdk


def get_client():
    """return client to handle authentication"""
    return globus_sdk.ConfidentialAppAuthClient(
        settings.SOCIAL_AUTH_GLOBUS_KEY, settings.SOCIAL_AUTH_GLOBUS_SECRET
    )


def get_transfer_client(user):
    """return a transfer client for the user"""
    client = user.get_credentials("globus")
    if client is not None:
        access_token = client.extra_data["transfer.api.globus.org"]["access_token"]
        authorizer = globus_sdk.AccessTokenAuthorizer(access_token)
        client = globus_sdk.TransferClient(authorizer=authorizer)
    return client


def list_tokens(tokens):
    """return a lookup of tokens organized by token and token type
    This function is first used to populate the Globus social auth
    extra_data field that holds the organized tokens
    """
    lookup = dict()
    tokens = [tokens] + tokens["other_tokens"]
    for token in tokens:
        lookup[token["resource_server"]] = dict()
        for token_type in ["id_token", "refresh_token", "access_token"]:
            if token_type in token:
                lookup[token["resource_server"]][token_type] = token[token_type]
    return lookup


def associate_user(user, client, code):
    """Here we do the following:

    1. Find the user's Globus account based on email. If the
       association doesn't exist, we create it.
    2. Update the token infos. We just save as extra data.
    """

    # Second step, get tokens from code
    tokens = client.oauth2_exchange_code_for_tokens(code)

    # Associate with the user account
    token_id = tokens.decode_id_token(client)

    # Look up the user based on token
    try:
        social = user.social_auth.get(provider="globus", uid=token_id["sub"])

    except UserSocialAuth.DoesNotExist:
        social = UserSocialAuth.objects.create(
            provider="globus", user=user, uid=token_id["sub"]
        )

    # Update with token_id infos
    social.extra_data = list_tokens(tokens.data)
    social.save()
    return user
