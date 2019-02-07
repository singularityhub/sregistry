'''

Copyright (C) 2017-2018 Vanessa Sochat.

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

# Python-social-auth

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'social_core.backends.username.UsernameAuth',
    'social_core.backends.open_id.OpenIdAuth',
    'social_core.backends.saml.SAMLAuth',
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.twitter.TwitterOAuth',
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.github.GithubOAuth2',
    'social_core.backends.gitlab.GitLabOAuth2',
    'social_core.backends.bitbucket.BitbucketOAuth2',
)


SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'shub.apps.users.views.social_user',
    'shub.apps.users.views.redirect_if_no_refresh_token',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',  # <--- must share same email
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)


SOCIAL_AUTH_LOGIN_REDIRECT_URL = 'http://127.0.0.1'

# http://psa.matiasaguirre.net/docs/configuration/settings.html#urls-options
#SOCIAL_AUTH_REDIRECT_IS_HTTPS = True

#SOCIAL_AUTH_USER_MODEL = 'django.contrib.auth.models.User'
#SOCIAL_AUTH_STORAGE = 'social.apps.django_app.me.models.DjangoStorage'
#SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
#SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/logged-in/'
#SOCIAL_AUTH_LOGIN_ERROR_URL = '/login-error/'
#SOCIAL_AUTH_LOGIN_URL = '/login-url/'
#SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/new-users-redirect-url/'
#SOCIAL_AUTH_LOGIN_REDIRECT_URL
#SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = '/new-association-redirect-url/'
#SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = '/account-disconnected-redirect-url/'
#SOCIAL_AUTH_INACTIVE_USER_URL = '/inactive-user/'

# On any admin or plugin login redirect to standard social-auth entry point for agreement to terms
LOGIN_REDIRECT_URL = '/login'
