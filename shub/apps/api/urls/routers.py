'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017 Vanessa Sochat.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from django.conf.urls import (
    url, 
    include
)

from rest_framework import routers

from shub.apps.api.urls.containers import ContainerViewSet
from shub.apps.api.urls.collections import CollectionViewSet
from shub.apps.api.actions.push import ContainerPushViewSet

router = routers.DefaultRouter()
router.register(r'^containers', ContainerViewSet, base_name="container")
router.register(r'^collections', CollectionViewSet, base_name="collection")
router.register(r'^push', ContainerPushViewSet, base_name="push")  # push

urlpatterns = [

    url(r'^', include(router.urls))

]
