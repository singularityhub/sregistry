'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from django.conf.urls import url
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
    url(r'^teams/new$', views.edit_team, name='new_team'),

]
