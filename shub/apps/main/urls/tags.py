"""

Copyright (C) 2017-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.conf.urls import url
import shub.apps.main.views as views

urlpatterns = [
    url(r"^tags/(?P<tid>\d+)/?$", views.view_tag, name="view_tag"),
    url(r"^tags/?$", views.all_tags, name="all_tags"),
    url(
        r"^collections/downloads/?$",
        views.collection_downloads,
        name="collection_downloads",
    ),
    url(r"^collections/stars/?$", views.collection_stars, name="collection_stars"),
    url(r"^favorite/(?P<cid>\d+)/?$", views.star_collection, name="favorite"),
    url(r"^tags/containers/(?P<cid>\d+)/add/?$", views.add_tag, name="add_tag"),
    url(
        r"^tags/containers/(?P<cid>\d+)/remove/?$", views.remove_tag, name="remove_tag"
    ),
]
