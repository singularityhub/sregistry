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

    # Share
    url(r'^containers/(?P<cid>\d+)/download/share/(?P<secret>.+?)/?$', views.download_share,name='download_share'),
    url(r'^containers/(?P<cid>\d+)/share/?$', views.generate_share,name='generate_share'),
 
    # Containers
    url(r'^tags/(?P<tid>.+?)/view/?$', views.view_tag,name='view_tag'),
    url(r'^containers/(?P<cid>\d+)/view/?$', views.view_container,name='view_container'),
    url(r'^containers/(?P<collection>.+?)/(?P<name>.+?):(?P<tag>.+?)/?$', views.view_named_container,name='view_container'),
    url(r'^containers/(?P<cid>\d+)/?$', views.container_details,name='container_details'),
    url(r'^containers/(?P<cid>\d+)/tags/?$', views.container_tags,name='container_tags'),
    url(r'^containers/(?P<cid>\d+)/delete/?$', views.delete_container,name='delete_container'),
    url(r'^containers/(?P<cid>\d+)/freeze/?$', views.change_freeze_status,name='change_freeze_status'),

    # Download
    url(r'^containers/(?P<cid>\d+)/download/recipe/?$', views.download_recipe,name='download_recipe'),
    url(r'^containers/(?P<cid>\d+)/download/(?P<secret>.+?)/?$', views.download_container,name='download_container'),

]

