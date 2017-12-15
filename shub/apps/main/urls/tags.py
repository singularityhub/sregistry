'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017 Vanessa Sochat.

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


    url(r'^tags/(?P<tid>\d+)/?$', views.view_tag,name='view_tag'),
    url(r'^tags/?$', views.all_tags,name='all_tags'),
    url(r'^collections/downloads/?$', views.collection_downloads,name='collection_downloads'),
    url(r'^collections/stars/?$', views.collection_stars,name='collection_stars'),
    url(r'^collections/(?P<cid>\d+)/favorite/?$', views.star_collection,name='favorite'),
    url(r'^tags/containers/(?P<cid>\d+)/add/?$', views.add_tag,name='add_tag'),
    url(r'^tags/containers/(?P<cid>\d+)/remove/?$', views.remove_tag,name='remove_tag'),

]

