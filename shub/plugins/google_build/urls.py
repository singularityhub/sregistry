"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.conf.urls import include, url
from shub.plugins.google_build import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"^build", views.RecipePushViewSet, base_name="build")  # build

urlpatterns = [
    url(r"^github/receive/?$", views.receive_hook, name="receive_hook"),
    url(r"^build/receive/(?P<cid>\d+)/?$", views.receive_build, name="receive_build"),
    url(
        r"^delete/container/(?P<cid>\d+)/?$",
        views.delete_container,
        name="delete_google_container",
    ),
    url(
        r"^delete/collection/(?P<cid>\d+)/?$",
        views.delete_collection,
        name="delete_google_collection",
    ),
    url(r"^github/save/?$", views.save_collection, name="save_collection"),
    url(r"^github/connect/?$", views.connect_github, name="google_build_connect"),
    url(r"^", include(router.urls)),
]
