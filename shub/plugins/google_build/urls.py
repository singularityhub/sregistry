"""

Copyright 2019-2023 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.urls import include, re_path
from rest_framework import routers

from shub.plugins.google_build import views

router = routers.DefaultRouter()
router.register(r"^build", views.RecipePushViewSet, basename="build")  # build

urlpatterns = [
    re_path(r"^github/receive/?$", views.receive_hook, name="receive_hook"),
    re_path(
        r"^build/receive/(?P<cid>\d+)/?$", views.receive_build, name="receive_build"
    ),
    re_path(
        r"^delete/container/(?P<cid>\d+)/?$",
        views.delete_container,
        name="delete_google_container",
    ),
    re_path(
        r"^delete/collection/(?P<cid>\d+)/?$",
        views.delete_collection,
        name="delete_google_collection",
    ),
    re_path(r"^github/save/?$", views.save_collection, name="save_collection"),
    re_path(r"^github/connect/?$", views.connect_github, name="google_build_connect"),
    re_path(r"^", include(router.urls)),
]
