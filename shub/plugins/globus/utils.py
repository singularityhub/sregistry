'''

Copyright (c) 2017, Vanessa Sochat, All rights reserved.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

'''

import pickle
from shub.apps.users.models import User
from social_django.models import UserSocialAuth
from django.contrib.auth import login
import requests
import globus_sdk
from django.conf import settings

def get_client():
    '''return client to handle authentication'''
    return globus_sdk.ConfidentialAppAuthClient(settings.SOCIAL_AUTH_GLOBUS_KEY,
                                                settings.SOCIAL_AUTH_GLOBUS_SECRET)


def get_transfer_client(user):
    '''return a transfer client for the user''' 
    client = user.get_credentials('globus')
    if client is not None:
        access_token = client.extra_data['transfer.api.globus.org']['access_token']
        authorizer = globus_sdk.AccessTokenAuthorizer(access_token)
        client = globus_sdk.TransferClient(authorizer=authorizer)
    return client


def list_tokens(tokens):
    '''return a lookup of tokens organized by token and token type
       This function is first used to populate the Globus social auth
       extra_data field that holds the organized tokens
    '''
    lookup = dict()
    tokens = [tokens] + tokens['other_tokens']
    for token in tokens:
        lookup[token['resource_server']] = dict()
        for token_type in ['id_token', 'refresh_token', 'access_token']:
            if token_type in token:
                lookup[token['resource_server']][token_type] = token[token_type]
    return lookup



def associate_user(user, client, code):
    ''' Here we do the following:

    1. Find the user's Globus account based on email. If the
       association doesn't exist, we create it.
    2. Update the token infos. We just save as extra data.
    '''

    # Second step, get tokens from code
    tokens = client.oauth2_exchange_code_for_tokens(code)

    # Associate with the user account
    token_id = tokens.decode_id_token(client)
 
    # Look up the user based on email
    email = token_id['email']
    try:
        social = user.social_auth.get(provider="globus",
                                      uid=token_id["sub"])

    except UserSocialAuth.DoesNotExist:
        social = UserSocialAuth.objects.create(provider="globus",
                                               user=user,
                                               uid=token_id["sub"])  

    # Update with token_id infos
    social.extra_data = list_tokens(tokens.data)
    social.save()  
    return user
