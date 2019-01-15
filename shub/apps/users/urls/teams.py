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

from django.conf.urls import url, include
from django.conf import settings
import shub.apps.users.views as views

urlpatterns = [

    url(r'^teams$', views.view_teams, name="teams"),
    url(r'^teams/(?P<tid>.+?)/view$', views.view_team, name="team_details"),
    url(r'^teams/(?P<tid>.+?)/edit$', views.edit_team, name="edit_team"),
    url(r'^teams/(?P<tid>.+?)/delete$', views.delete_team, name="delete_team"),
    url(r'^teams/(?P<tid>.+?)/invite$', views.generate_team_invite, name="generate_team_invite"),
    url(r'^teams/(?P<tid>.+?)/(?P<code>.+?)/join$', views.join_team, name="join_team"),
    url(r'^teams/(?P<tid>.+?)/join$', views.join_team, name="join_team"),
    url(r'^teams/(?P<tid>.+?)/leave$', views.leave_team, name="leave_team"),

    # Remove members and owners
    url(r'^teams/(?P<tid>.+?)/remove/member/(?P<uid>.+?)$', views.remove_member, name="remove_member"),
    url(r'^teams/(?P<tid>.+?)/remove/owner/(?P<uid>.+?)$', views.remove_owner, name="remove_owner"),

    # Add members and owners
    url(r'^teams/(?P<tid>.+?)/add/owner/(?P<uid>.+?)$', views.add_owner, name="remove_owner"),

    url(r'^teams/new$',views.edit_team,name='new_team'),

]
