"""
Github OAuth2 backend, docs at:
    https://python-social-auth.readthedocs.io/en/latest/backends/github.html
"""
from urllib.parse import urlencode
from requests import HTTPError

from six.moves.urllib.parse import urljoin

from social_core.backends.oauth import BaseOAuth2
from social_core.exceptions import AuthFailed

from django.conf import settings
from shub.logger import bot

import base64


class KeyrockOAuth2(BaseOAuth2):
    """Keyrock OAuth authentication backend"""
    name = 'fiware'
    AUTHORIZATION_URL = urljoin(
        settings.FIWARE_IDM_ENDPOINT, '/oauth2/authorize')
    ACCESS_TOKEN_URL = urljoin(settings.FIWARE_IDM_ENDPOINT, '/oauth2/token')
    #LOGOUT_URL = urljoin(settings.FIWARE_IDM_ENDPOINT, '/auth/logout')
    ACCESS_TOKEN_METHOD = 'POST'

    REDIRECT_STATE = False

    EXTRA_DATA = [
        ('id', 'username'),
        ('id', 'uid')
    ]

    def get_user_id(self, details, response):
        return response['id']

    def get_user_details(self, response):
        """Return user details from FI-WARE account"""
        bot.debug( {'username': response.get('id'),
                'email': response.get('email') or '',
                'fullname': response.get('displayName') or ''})
        return {'username': response.get('id'),
                'email': response.get('email') or '',
                'fullname': response.get('displayName') or ''}

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        url = urljoin(settings.FIWARE_IDM_ENDPOINT, '/user?' + urlencode({
            'access_token': access_token
        }))
        bot.debug(self.get_json(url))
        return self.get_json(url)

    def auth_headers(self):
        response = super(KeyrockOAuth2, self).auth_headers()

        keys = settings.SOCIAL_AUTH_FIWARE_KEY + \
            ":" + settings.SOCIAL_AUTH_FIWARE_SECRET
        authorization_basic = base64.b64encode(
            keys.encode('ascii')).decode('ascii')
        response['Authorization'] = 'Basic ' + authorization_basic

        bot.debug(response)
        return response

    def auth_complete_params(self, state=None):
        # response = super(KeyrockOAuth2, self).auth_complete_params(state)
        # response['grant_type'] = 'authorization_code' + \
        #     '&code=' + response['code'] + \
        #     '&redirect_uri=' + response['redirect_uri']
        # return response

        bot.debug( {
            'grant_type': 'authorization_code',  # request auth code
            'code': self.data.get('code', ''),  # server response code
            'redirect_uri': self.get_redirect_uri(state)
        } )
        return {
            'grant_type': 'authorization_code',  # request auth code
            'code': self.data.get('code', ''),  # server response code
            'redirect_uri': self.get_redirect_uri(state)
        }
