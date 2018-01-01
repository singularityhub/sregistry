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
from shub.apps.main.query import collection_query

urlpatterns = [

    url(r'^collections/?$', views.all_collections, name="collections"),
    url(r'^collections/(?P<cid>\d+)/edit/?$',views.edit_collection,name='edit_collection'),
    url(r'^collections/(?P<cid>\d+)/?$',views.view_collection,name='collection_details'),
    url(r'^collections/my/?$',views.my_collections,name='my_collections'),
    url(r'^collections/(?P<cid>\d+)/usage/?$', views.collection_commands,name='collection_commands'),
    url(r'^collections/(?P<cid>\d+)/delete/?$', views.delete_collection,name='delete_collection'),
    url(r'^collections/(?P<cid>\d+)/private/?$',views.make_collection_private,name='make_collection_private'),
    url(r'^collections/(?P<cid>\d+)/public/?$',views.make_collection_public,name='make_collection_public')

]

