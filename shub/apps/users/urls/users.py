'''

Copyright (C) 2017-2019 Vanessa Sochat.

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
import shub.apps.users.views as views


urlpatterns = [

    url(r'^terms/agree', views.agree_terms, name="agree_terms"),
    url(r'^token', views.view_token, name="token"),
    url(r'^u/profile', views.view_profile, name="profile"),
    #url(r'^(?P<username>[A-Za-z0-9@/./+/-/_]+)/$',views.view_profile,name="profile"),

]

