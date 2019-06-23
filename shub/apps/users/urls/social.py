'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from django.conf.urls import url, include
import shub.apps.users.views as user_views
from social_django import urls as social_urls

urlpatterns = [

    # Twitter, and social auth
    url(r'^login/$', user_views.login, name="login"),
    url(r'^accounts/login/$', user_views.login),
    url(r'^logout/$', user_views.logout, name="logout"),
    url('', include(social_urls, namespace='social')),

]
