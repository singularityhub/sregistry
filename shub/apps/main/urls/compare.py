"""

Copyright 2017-2023 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""


from django.urls import re_path

import shub.apps.main.views as views

urlpatterns = [
    re_path(
        r"^tools/sizes/?$", views.collections_treemap, name="containers_treemap"
    ),  # also redirects to collections_treemap view
    re_path(
        r"^data/containers/sizes/csv/?$",
        views.container_size_data,
        name="container_size_data",
    ),
    re_path(
        r"^data/collections/sizes/csv/?$",
        views.collection_size_data,
        name="collections_size_data",
    ),
]
