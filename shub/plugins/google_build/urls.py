'''

Copyright (C) 2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from django.conf.urls import include, url
from shub.plugins.google_build import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'^build', views.RecipePushViewSet, base_name="build")  # build

urlpatterns = [
    url(r'^', include(router.urls))
]
