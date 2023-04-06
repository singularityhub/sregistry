"""

Copyright 2017-2023 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.urls import re_path

import shub.apps.main.views as views

urlpatterns = [
    re_path(r"^collections/?$", views.all_collections, name="collections"),
    re_path(
        r"^collections/(?P<cid>\d+)/edit/?$",
        views.edit_collection,
        name="edit_collection",
    ),
    re_path(r"^collections/new/?$", views.new_collection, name="new_collection"),
    re_path(
        r"^collections/(?P<cid>\d+)/settings/?$",
        views.collection_settings,
        name="collection_settings",
    ),
    re_path(
        r"^collections/(?P<cid>\d+)/contributors/?$",
        views.edit_contributors,
        name="edit_contributors",
    ),
    re_path(
        r"^collections/(?P<cid>\d+)/?$",
        views.view_collection,
        name="collection_details",
    ),
    re_path(r"^collections/my/?$", views.my_collections, name="my_collections"),
    re_path(
        r"^collections/(?P<cid>\d+)/usage/?$",
        views.collection_commands,
        name="collection_commands",
    ),
    re_path(
        r"^collections/(?P<cid>\d+)/delete/?$",
        views.delete_collection,
        name="delete_collection",
    ),
    re_path(
        r"^collections/(?P<cid>\d+)/private/?$",
        views.make_collection_private,
        name="make_collection_private",
    ),
    re_path(
        r"^collections/(?P<cid>\d+)/public/?$",
        views.make_collection_public,
        name="make_collection_public",
    ),
    re_path(
        r"^collections/(?P<username>.+?)/(?P<reponame>.+?)/?$",
        views.view_named_collection,
        name="collection_byname",
    ),
]
