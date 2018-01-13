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


    url(r'^labels/(?P<lid>\d+)/?$', views.view_label,name='view_label_id'),
    url(r'^labels/key/(?P<key>.+?)/value/(?P<value>.+?)/?$', views.view_label_keyval, name='view_label'),
    url(r'^labels/key/(?P<key>.+?)/?$', views.view_label_key,name='view_label_key'),
    url(r'^labels/?$', views.all_labels,name='all_labels'),

]

