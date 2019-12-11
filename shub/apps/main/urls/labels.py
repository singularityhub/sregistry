"""

Copyright (C) 2017-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.conf.urls import url
import shub.apps.main.views as views

urlpatterns = [
    url(r"^labels/(?P<lid>\d+)/?$", views.view_label, name="view_label_id"),
    url(
        r"^labels/key/(?P<key>.+?)/value/(?P<value>.+?)/?$",
        views.view_label_keyval,
        name="view_label",
    ),
    url(r"^labels/key/(?P<key>.+?)/?$", views.view_label_key, name="view_label_key"),
    url(r"^labels/?$", views.all_labels, name="all_labels"),
]
