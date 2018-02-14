'''

Copyright (C) 2017-2018 The Board of Trustees of the Leland Stanford Junior
University.
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
from shub.apps.main.query import collection_query

urlpatterns = [

    url(r'^collections/?$', views.all_collections, name="collections"),
    url(r'^collections/(?P<cid>\d+)/edit/?$',views.edit_collection,name='edit_collection'),
    url(r'^collections/(?P<cid>\d+)/settings/?$',views.collection_settings,name='collection_settings'),
    url(r'^collections/(?P<cid>\d+)/?$',views.view_collection,name='collection_details'),
    url(r'^collections/my/?$',views.my_collections,name='my_collections'),
    url(r'^collections/(?P<cid>\d+)/usage/?$', views.collection_commands,name='collection_commands'),
    url(r'^collections/(?P<cid>\d+)/delete/?$', views.delete_collection,name='delete_collection'),
    url(r'^collections/(?P<cid>\d+)/private/?$',views.make_collection_private,name='make_collection_private'),
    url(r'^collections/(?P<cid>\d+)/public/?$',views.make_collection_public,name='make_collection_public')

]

