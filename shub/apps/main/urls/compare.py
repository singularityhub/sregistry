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

    url(r'^tools/sizes/?$',views.containers_treemap,name='containers_treemap'), # also redirects to collections_treemap view
    url(r'^tools/collection/(?P<cid>\d+)/sizes/?$',views.collection_treemap,name='collection_treemap'),  # containers in single collection
    url(r'^data/containers/sizes/csv/?$',views.container_size_data,name='container_size_data'),
    url(r'^data/collections/sizes/csv/?$',views.collection_size_data,name='collections_size_data'),
    url(r'^data/collections/(?P<cid>\d+)/sizes/csv/?$',views.single_collection_size_data,name='collection_size_data'),

]
