"""

Copyright (C) 2017-2021 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.conf.urls import url, include
import rest_framework.authtoken.views as authviews

from rest_framework import routers
from shub.apps.api.urls.containers import ContainerViewSet
from shub.apps.api.urls.collections import CollectionViewSet
from shub.apps.api.actions.push import collection_auth_check
from shub.apps.api.actions.upload import UploadUI, upload_complete

router = routers.DefaultRouter()
router.register(r"^containers", ContainerViewSet, base_name="container")
router.register(r"^collections", CollectionViewSet, base_name="collection")

urlpatterns = [
    url(r"^", include(router.urls)),
    url(r"^api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    url(r"^api-token-auth/", authviews.obtain_auth_token),
    url(
        r"^upload/chunked_upload/?$",
        collection_auth_check,
        name="collection_auth_check",
    ),
    url(r"^upload/(?P<cid>.+?)/?$", UploadUI.as_view(), name="chunked_upload"),
    url(r"^uploads/complete/?$", upload_complete, name="terminal_upload_complete"),
]
