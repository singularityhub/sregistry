'''

Copyright (C) 2017-2018 Vanessa Sochat.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
