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

from django.views.generic.base import TemplateView
from django.conf.urls import url
import shub.apps.base.views as views

urlpatterns = [
    url(r'^$', views.index_view, name="index"),
    url(r'^about$', views.about_view, name="about"),
    url(r'^tools$', views.tools_view, name="tools"),
    url(r'^terms$', views.terms_view, name="terms"),
    url(r'^robots\.txt/$',TemplateView.as_view(template_name='base/robots.txt', 
                                               content_type='text/plain')),
]
