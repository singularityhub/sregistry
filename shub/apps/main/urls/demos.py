'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017 Vanessa Sochat.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''


from django.conf.urls import url
import shub.apps.main.views as views

urlpatterns = [

    url(r'^collection/demos/(?P<cid>\d+)/?$', views.collection_demos,name='collection_demos'),
    url(r'^demos/(?P<did>\d+)/?$', views.view_demo,name='view_demo'),
    url(r'^demos/(?P<cid>\d+)/(?P<did>.+?)/edit$/?$', views.edit_demo,name='edit_demo'),
    url(r'^demos/(?P<cid>\d+)/new/?$$', views.edit_demo,name='new_demo')

]

