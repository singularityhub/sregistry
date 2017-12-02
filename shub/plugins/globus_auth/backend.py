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

from social_core.backends.oauth import BaseOAuth2
from social_core.utils import handle_http_errors
from social_core.exceptions import AuthMissingParameter
from shub.logger import bot
from shub.apps.users.utils import create_code_challenge
import pickle
import globus_sdk

class GlobusOAuth2(BaseOAuth2):
    '''OAuth2 Backend for Globus
       https://docs.globus.org/api/auth/developer-guide/#obtaining-authorization

     # Authorization request
       https://auth.globus.org/v2/oauth2/authorize 

     # to get a token from code
       https://auth.globus.org/v2/oauth2/token 
     '''
    name = 'globus'
    API_URL = "https://auth.globus.org/v2/oauth2"
    AUTHORIZATION_URL = "https://auth.globus.org/v2/oauth2/authorize"
    ACCESS_TOKEN_URL = "https://auth.globus.org/v2/oauth2/token"
    ACCESS_TOKEN_METHOD = 'POST'

    # Defaults can remove
    #REFRESH_TOKEN_URL = None
    #REFRESH_TOKEN_METHOD = 'POST'
    #RESPONSE_TYPE = 'code'
    #REDIRECT_STATE = True
    #STATE_PARAMETER = True
    #CODE_VERIFIER = uuid.uuid4()

    # If you need to customize per deployment, define this in settings/secrets.py
    # as SOCIAL_AUTH_GLOBUS_SCOPE and do not repeat here
    DEFAULT_SCOPE = ["openid",
                     "profile",
                     "email",
                     "urn:globus:auth:scope:transfer.api.globus.org:all"]
    EXTRA_DATA = [
        ('refresh_token', 'refresh_token', True),
        ('expires_in', 'expires'),
        ('verifier', 'verifier'),
        ('token_type', 'token_type', True)
    ]

    def api_url(self):
        return self.API_URL

    def get_user_details(self, response):
        '''return Globus user details'''
        bot.info(response)
        return {'username': response.get('preferred_username'),
                'email': response.get('email') or '',
                'fullname': response.get('name')}


# STOPPED HERE - look at line 373 and find where/how we are requesting an access token.

    def auth_complete_params(self, state=None):
        '''
        The request to get a token should look like the following

          self.auth_client.oauth2_token(
            {'client_id': self.client_id,
             'grant_type': 'authorization_code',
             'code': auth_code.encode('utf-8'),
             'code_verifier': self.verifier,
             'redirect_uri': self.redirect_uri})
        '''
        params = super(GlobusOAuth2, self).auth_complete_params(state)
        print(params)
        if self.data.get('access_token'):
            # Don't add postmessage if this is plain server-side workflow
            params['redirect_uri'] = 'postmessage'
        params['grant_type'] = 'authorization_code'
        params['client_id'] = self.strategy.get_session('id')
        params['code_verifier'] = self.strategy.get_session('verifier')
        return params

    @handle_http_errors
    def auth_complete(self, *args, **kwargs):

        print('STARTING AUTH COMPLETE')

        # Get state, verifier, etc.
        verifier = self.strategy.session_get('verifier')
        state = self.data.get('state')
        code = self.data.get('code')

        # THIS is where we are crashing and failing
        print(self.auth_headers())
        print(self.auth_complete_params())
        print(self.data)
        print(self.strategy.__dict__)

        if 'code' in self.data:
            response = self.request_access_token(

                self.ACCESS_TOKEN_URL,
                data=self.auth_complete_params(),
                headers=self.auth_headers(),
                method=self.ACCESS_TOKEN_METHOD

            )
            self.process_error(response)
            return self.do_auth(response['access_token'],
                                response=response,
                                *args, **kwargs)

        else:
            raise AuthMissingParameter(self, 'access_token, id_token, or code')


    def request_access_token(self, *args, **kwargs):
        data = super(GlobusOAuth2, self).request_access_token(*args, **kwargs)
        data.update({'access_token': data['token']})
        return data


    def auth_extra_arguments(self):
        '''Return extra arguments needed on auth process. The defaults can be
        overriden by GET parameters.'''
        extra_arguments = super(GlobusOAuth2, self).auth_extra_arguments()

        # Must be fresly generated on every request
        verifier, challenge = create_code_challenge()
        self.strategy.session_set('verifier', verifier)
        extra_arguments.update({'code_challenge': challenge,
                                'code_challenge_method': 'S256',
                                'access_type': 'online' })
        return extra_arguments

    def get_user_id(self, details, response):
        bot.debug(details)
        return details['sub']

    def auth_complete_params(self, state=None):
        bot.info(self.data)

        return {
            'code_challenge_method':'S256',
            'code_verifier': self.strategy.session_get('verifier'),
            'grant_type': 'authorization_code',
            'code': self.data.get('code', ''),
            'client_id': self.get_key_and_secret()[0]
        }

    def user_data(self, access_token, path=None, *args, **kwargs):
        """Loads user data from service"""

        userinfo = self.get_json(
                        'https://auth.globus.org/v2/oauth2/userinfo',
                        params={'access_token': access_token}
                       )
        print(userinfo)
        return userinfo
