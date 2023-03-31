"""

Copyright 2019-2023 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

Modified from: https://github.com/mugwort-rc/django-pgpdb
Commit: 763c2708c16bf58064f741ceb2e2ab752dea3663 (no LICENSE)

"""

from django.urls import re_path

from shub.plugins.pgp import views

urlpatterns = [
    re_path(r"^add/?$", views.add, name="add"),
    re_path(r"^lookup/?$", views.lookup, name="lookup"),
]
