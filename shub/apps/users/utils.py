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

from rest_framework.authtoken.models import Token
import hashlib
import base64
import os

def get_usertoken(user):
    try:
        token = Token.objects.get(user=user)
    except TokenDoesNotExist:
        token = Token.objects.create(user=user)
    return token.key

def create_code_challenge():
    '''This function will produce a verifier and challenge for Native Application
    flow with OAuth2. We always use SHA256 and the code verifier is between 43
    and 128 in length.

    verifier: an unhashed secret
    challenge: a base64 encoded (hashed) version, sent at the start
        Must only contain the following characters: [a-zA-Z0-9~_.-].

    derived from https://github.com/globus/globus-sdk-python/blob/master/globus_sdk/auth/oauth2_native_app.py
    '''
    code_verifier = base64.urlsafe_b64encode(
                         os.urandom(32)).decode('utf-8').rstrip('=')

    hashed_verifier = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    # urlsafe base64 encode that hash and strip the padding
    code_challenge = base64.urlsafe_b64encode(
        hashed_verifier).decode('utf-8').rstrip('=')

    # return the verifier and the encoded hash
    return code_verifier, code_challenge
