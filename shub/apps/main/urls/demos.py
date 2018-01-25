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

urlpatterns = [

    url(r'^collection/demos/(?P<cid>\d+)/?$', views.collection_demos,name='collection_demos'),
    url(r'^demos/(?P<did>\d+)/?$', views.view_demo,name='view_demo'),
    url(r'^demos/(?P<cid>\d+)/(?P<did>.+?)/edit$/?$', views.edit_demo,name='edit_demo'),
    url(r'^demos/(?P<cid>\d+)/new/?$$', views.edit_demo,name='new_demo')

]

