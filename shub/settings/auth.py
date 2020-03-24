"""

Copyright (C) 2017-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

# Python-social-auth

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "social_core.backends.username.UsernameAuth",
    "social_core.backends.open_id.OpenIdAuth",
    "social_core.backends.saml.SAMLAuth",
    "social_core.backends.google.GoogleOAuth2",
    "social_core.backends.twitter.TwitterOAuth",
    "social_core.backends.facebook.FacebookOAuth2",
    "shub.apps.users.views.auth.ShubGithubOAuth2",
    # "social_core.backends.github.GithubOAuth2",
    "social_core.backends.gitlab.GitLabOAuth2",
    "social_core.backends.bitbucket.BitbucketOAuth2",
)


SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "shub.apps.users.views.social_user",
    "shub.apps.users.views.redirect_if_no_refresh_token",
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.social_auth.associate_by_email",  # <--- must share same email
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
)


SOCIAL_AUTH_LOGIN_REDIRECT_URL = "http://127.0.0.1"

# http://psa.matiasaguirre.net/docs/configuration/settings.html#urls-options
# SOCIAL_AUTH_REDIRECT_IS_HTTPS = True

# SOCIAL_AUTH_USER_MODEL = 'django.contrib.auth.models.User'
# SOCIAL_AUTH_STORAGE = 'social.apps.django_app.me.models.DjangoStorage'
# SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
# SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/logged-in/'
# SOCIAL_AUTH_LOGIN_ERROR_URL = '/login-error/'
# SOCIAL_AUTH_LOGIN_URL = '/login-url/'
# SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/new-users-redirect-url/'
# SOCIAL_AUTH_LOGIN_REDIRECT_URL
# SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = '/new-association-redirect-url/'
# SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = '/account-disconnected-redirect-url/'
# SOCIAL_AUTH_INACTIVE_USER_URL = '/inactive-user/'

# On any admin or plugin login redirect to standard social-auth entry point for agreement to terms
LOGIN_REDIRECT_URL = "/login"
