"""

Copyright 2017-2023 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.urls import re_path

import shub.apps.main.views as views

urlpatterns = [
    # Share
    re_path(
        r"^containers/(?P<cid>\d+)/download/share/(?P<secret>.+?)/?$",
        views.download_share,
        name="download_share",
    ),
    re_path(
        r"^containers/(?P<cid>\d+)/share/?$",
        views.generate_share,
        name="generate_share",
    ),
    # Containers
    re_path(r"^tags/(?P<tid>.+?)/view/?$", views.view_tag, name="view_tag"),
    re_path(
        r"^containers/(?P<cid>\d+)/view/?$", views.view_container, name="view_container"
    ),
    re_path(
        r"^containers/(?P<collection>.+?)/(?P<name>.+?):(?P<tag>.+?)/?$",
        views.view_named_container,
        name="view_container",
    ),
    re_path(
        r"^containers/(?P<cid>\d+)/?$",
        views.container_details,
        name="container_details",
    ),
    re_path(
        r"^containers/(?P<cid>\d+)/tags/?$", views.container_tags, name="container_tags"
    ),
    re_path(
        r"^containers/(?P<cid>\d+)/delete/?$",
        views.delete_container,
        name="delete_container",
    ),
    re_path(
        r"^containers/(?P<cid>\d+)/freeze/?$",
        views.change_freeze_status,
        name="change_freeze_status",
    ),
    # Download
    re_path(
        r"^containers/(?P<cid>\d+)/download/recipe/?$",
        views.download_recipe,
        name="download_recipe",
    ),
    re_path(
        r"^containers/(?P<cid>\d+)/download/(?P<secret>.+?)/?$",
        views.download_container,
        name="download_container",
    ),
]
