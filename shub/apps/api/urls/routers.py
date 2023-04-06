"""

Copyright 2017-2023 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

import rest_framework.authtoken.views as authviews
from django.urls import include, re_path
from rest_framework import routers

from shub.apps.api.actions.push import collection_auth_check
from shub.apps.api.actions.upload import UploadUI, upload_complete
from shub.apps.api.urls.collections import CollectionViewSet
from shub.apps.api.urls.containers import ContainerViewSet

router = routers.DefaultRouter()
router.register(r"^containers", ContainerViewSet, basename="container")
router.register(r"^collections", CollectionViewSet, basename="collection")

urlpatterns = [
    re_path(r"^", include(router.urls)),
    re_path(r"^api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    re_path(r"^api-token-auth/", authviews.obtain_auth_token),
    re_path(
        r"^upload/chunked_upload/?$",
        collection_auth_check,
        name="collection_auth_check",
    ),
    re_path(r"^upload/(?P<cid>.+?)/?$", UploadUI.as_view(), name="chunked_upload"),
    re_path(r"^uploads/complete/?$", upload_complete, name="terminal_upload_complete"),
]
