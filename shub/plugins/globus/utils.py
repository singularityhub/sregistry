'''

Copyright (c) 2017, Vanessa Sochat, All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''

import pickle
from shub.apps.users.models import User
from social_django.models import UserSocialAuth
from django.contrib.auth import login
import requests
import globus_sdk

from shub.settings import (
    SOCIAL_AUTH_GLOBUS_KEY,
    SOCIAL_AUTH_GLOBUS_SECRET
)

def get_client():
    '''return client to handle authentication'''
    return globus_sdk.ConfidentialAppAuthClient(SOCIAL_AUTH_GLOBUS_KEY,
                                                SOCIAL_AUTH_GLOBUS_SECRET)

def list_tokens(credentials):
    '''return a list of tokens organized by token and token type
    '''
    token_list = []
    tokens = credentials.extra_data
    tokens = [tokens] + tokens['other_tokens']
    for token in tokens:
        for token_type in ['id_token', 'refresh_token', 'access_token']:
            if token_type in token:
                token_list = token_list + [(token[token_type],token_type)]
    return token_list



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
    social.extra_data = tokens.data
    social.save()  
    return user
