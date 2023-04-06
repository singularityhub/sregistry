"""

Copyright 2017-2023 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.urls import include, re_path
from social_django import urls as social_urls

import shub.apps.users.views as user_views

urlpatterns = [
    # Twitter, and social auth
    re_path(r"^login/$", user_views.login, name="login"),
    re_path(r"^accounts/login/$", user_views.login),
    re_path(r"^logout/$", user_views.logout, name="logout"),
    re_path("", include(social_urls, namespace="social")),
]
