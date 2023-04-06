"""

Copyright 2017-2023 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.urls import re_path

import shub.apps.main.views as views

urlpatterns = [
    re_path(r"^labels/(?P<lid>\d+)/?$", views.view_label, name="view_label_id"),
    re_path(
        r"^labels/key/(?P<key>.+?)/value/(?P<value>.+?)/?$",
        views.view_label_keyval,
        name="view_label",
    ),
    re_path(
        r"^labels/key/(?P<key>.+?)/?$", views.view_label_key, name="view_label_key"
    ),
    re_path(r"^labels/?$", views.all_labels, name="all_labels"),
]
