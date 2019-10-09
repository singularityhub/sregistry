'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from django.conf.urls import url
import shub.apps.users.views as views


urlpatterns = [

    url(r'^terms/agree$', views.agree_terms, name="agree_terms"),

    # Only provided to be compatible with Sylabs /auth/tokens
    url(r'^token$', views.view_token, name="token"),
    url(r'^auth/tokens$', views.view_token, name="tokens"),
    url(r'^token/update$', views.update_token, name="update_token"),
    url(r'^u/profile$', views.view_profile, name="profile"),
    url(r'^u/delete$', views.delete_account, name="delete_account"),  # delete account
    url(r'^u/profile/(?P<username>.+)$', views.view_profile,name="profile"),
]
