"""

Copyright 2017-2023 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.urls import re_path

import shub.apps.users.views as views

urlpatterns = [
    re_path(r"^terms/agree$", views.agree_terms, name="agree_terms"),
    # Only provided to be compatible with Sylabs /auth/tokens
    re_path(r"^token$", views.view_token, name="token"),
    re_path(r"^auth/tokens$", views.view_token, name="tokens"),
    re_path(r"^token/update$", views.update_token, name="update_token"),
    re_path(r"^u/profile$", views.view_profile, name="profile"),
    re_path(
        r"^u/delete$", views.delete_account, name="delete_account"
    ),  # delete account
    re_path(r"^u/profile/(?P<username>.+)$", views.view_profile, name="profile"),
]
