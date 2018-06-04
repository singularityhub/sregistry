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

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import (
    HttpResponseRedirect,
    JsonResponse
)

from shub.settings import USER_COLLECTIONS
from shub.apps.users.forms import TeamForm
from shub.apps.users.models import ( User, Team, MembershipInvite )
from shub.apps.users.permissions import ( 
    has_create_permission, 
    is_invite_valid 
)
from shub.apps.users.utils import get_user

import uuid


def get_team(tid):
    ''' get a team based on its primary id

       Parameters
       ==========
       tid: the id of the team to look up

   '''
    keyargs = {'id': tid}
    try:
        team = Team.objects.get(**keyargs)
    except Team.DoesNotExist:
        raise Http404
    else:
        return team



################################################################################
# TEAM VIEWS ###################################################################
################################################################################


@login_required
def edit_team(request, tid=None):
    '''edit_team is the view to edit an existing team, or create a new team.
    :parma tid: the team id to edit or create. If none, indicates a new team
    '''
 
    if tid:
        team = get_team(tid)
        edit_permission = team.has_edit_permission(request)
        title = "Edit Team" 
    else:
        team = Team()
        edit_permission = True
        title = "New Team"

    if edit_permission:

        form = TeamForm(request.POST or None, 
                        request.FILES or None,
                        instance=team)

        if form.is_valid():
            form.save()

            # An editor is always a member
            if request.user not in team.members.all():
                team.members.add(request.user)
                team.save()

            # If a team id was provided, we add request user as owner
            if not tid:
                team.owners.add(request.user)
                team.save()

            messages.info(request, 'Team updated.')

        context = {"form": form,
                   "edit_permission": edit_permission,
                   "title":title,
                   "team":team}

        return render(request, "teams/edit_team.html", context)

    # If user makes it down here, does not have permission
    messages.info(request, "Only team owners can edit teams.")
    return redirect("teams")


def view_teams(request):
    '''view all teams (log in not required)
    :parma tid: the team id to edit or create. If none, indicates a new team
    '''
    teams = Team.objects.all()

    # Does the user have permission to create a team?
    create_permission = has_create_permission(request)

    context = {"teams": teams,
               "has_create_permission" : create_permission }

    return render(request, "teams/all_teams.html", context)


@login_required
def view_team(request, tid, code=None):
    '''view the details about a team
    :parma tid: the team id to edit or create. If none, indicates a new team
    '''
    team = get_team(tid)

    # Need to create annotation counts with "total" for all members
    edit_permission = team.has_edit_permission(request)
    members = team.get_members()
    count = len(members)

    context = {"team": team,
               "edit_permission":edit_permission,
               "count": count,
               "members": members,
               "code": code}

    return render(request, "teams/team_details.html", context)


################################################################################
# TEAM REQUESTS ################################################################
################################################################################


@login_required
def join_team(request, tid, code=None):
    '''add a user to a new team. If the team is open, he/she can join without
       needing a code. If is invite only, the code must be checked.

       Parameters
       ==========
       tid: the team id to edit or create. If none, indicates a new team
       code: if the user is accessing an invite link, the code is checked
             against the generated request.
    '''

    team = get_team(tid)
    user = request.user
    add_user = True
            
    if team.permission == "invite":
        if code is None:
            messages.info(request, "This is not a valid invitation.")
            add_user = False
        else:    
            add_user = is_invite_valid(team, code)
            if add_user is False:
                messages.info(request, "This code is invalid to join this team.")

    if add_user:   

        if user not in team.get_members():
            team.members.add(user)
            team.save()
            messages.info(request,"You have been added to team %s" %(team.name))
        else:
            messages.info(request,"You are already a member of %s" %(team.name))

    return HttpResponseRedirect(team.get_absolute_url())



################################################################################
# TEAM ACTIONS #################################################################
################################################################################


@login_required
def leave_team(request, tid):
    '''leave team is the view for a user to leave his or her team. A user
       doesn't need permission to remove him or herself.

       Parameters
       ==========
       team: the team to remove the individual from
    '''
    team = get_team(tid)

    team = _remove_member(team, request.user)
    team = _remove_owner(team, request.user)

    return redirect('teams')


def _remove_member(team, user):
    '''remove a member from a team if they are a part of it.
   
       Parameters
       ==========
       team: the team to remove the individual from
       user: the user to remove
    '''
    if user in team.members.all():
        team.members.remove(user)
        messages.info('%s is removed from %s' %(user.username, team.name))
        team.save()
    return team


def _remove_owner(team, user):
    '''remove an owner from a team, if they are part of it, and there
       is at least one other owner remaining.
   
       Parameters
       ==========
       team: the team to remove the individual from
       user: the user to remove
    '''
    if team.owners.count() > 1 and user in team.owners.all():
        team.owners.remove(user)
        messages.info('%s is no longer owner of %s' %(user.username, team.name))
        team.save()
    else:
        messages.info('At least one owner must be present for a team.')

    return team


@login_required
def remove_member(request, tid, uid):
    '''remove a member from a team.
 
       Parameters
       ==========
       team: the team to remove the individual from
       user: the user to remove
    '''
    
    team = get_team(tid)
    member = get_user(uid)

    if request.user in team.owners.all():
        team = _remove_member(team, member)
    else:
        message = "You are not allowed to perform this action."
    return JsonResponse({"message":message})


@login_required
def remove_owner(request, tid, uid):
    '''remove a member from a team.
 
       Parameters
       ==========
       tid: the team id to remove the individual from
       uid: the user id to remove
    '''
    
    team = get_team(tid)
    member = get_user(uid)

    if request.user in team.owners.all():
        team = _remove_owner(team, member)
    else:
        message = "You are not allowed to perform this action."
    return JsonResponse({"message":message})


@login_required
def add_owner(request, tid, uid):
    '''promote a user to be owner of a team
 
       Parameters
       ==========
       tid: the team id to remove the individual from
       uid: the user id to remove
    '''
    
    team = get_team(tid)
    member = get_user(uid)

    if request.user in team.owners.all():
        team.owners.add(member)
        team.save()
    else: 
        message = "You are not allowed to perform this action."
    return JsonResponse({"message":message})


@login_required
def delete_team(request, tid):
    '''delete a team entirely, must be an owner

       Parameters
       ==========
       tid: the team id

    '''
    team = get_team(tid)

    if request.user in team.owners.all():
        messages.info(request,'%s has been deleted.' %team.name)
        team.delete()
    else:
        messages.info(request, "You are not allowed to perform this action.")

    return redirect('teams')


@login_required
def generate_team_invite(request, tid):
    '''generate an invitation for a user, return to view.
       The invitation is valid for a day.
    '''
    team = get_team(tid)
    if request.user in team.owners.all():
        code = uuid.uuid4()
        new_invite = MembershipInvite.objects.create(team=team,
                                                     code=code)
        new_invite.save()
        url = new_invite.get_url()
        messages.info(request, 'This invitation is valid until use: %s' %url)
        return view_team(request, team.id, code=code)

    messages.info(request, "You do not have permission to invite to this team.")
    return HttpResponseRedirect(team.get_absolute_url())
