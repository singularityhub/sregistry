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

from shub.apps.users.models import ( User, Team )
from shub.apps.users.forms import TeamForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from shub.settings import USER_COLLECTIONS
from django.http import HttpResponseRedirect

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

    # Only an owner is allowed to edit a team
    if edit_permission:

        if request.method == "POST":

            form = TeamForm(request.POST,
                            request.FILES,
                            instance=team)

            if form.is_valid():
                team = form.save(commit=False)
    
                # We will get integrity error if already exists
                try:
                    team.save()

                    # An editor is always a member
                    team.contributors.add(request.user)

                    # If it's a new team, we add owner
                    if not tid:
                        team.owners.add(request.user)
                    team.save()

                    return HttpResponseRedirect(team.get_absolute_url())

                except:
                    message = "The name %s is already taken!" %team.name
                    messages.info(request, message)


        else:
            form = TeamForm(instance=team)

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
    context = {"teams": teams}
    return render(request, "teams/all_teams.html", context)


def view_users(request):
    '''view all users
    '''
    users = User.objects.all()
    lookups = []
    for user in users:
        if user.username != "AnonymousUser":
            userinfo = {'team': user.team_members.first(),
                        'name':user.username,
                        'id':user.id}
            lookups.append(userinfo)

    context = {"users": lookups}
    return render(request, "users/all_users.html", context)


@login_required
def view_team(request, tid, code=None):
    '''view the details about a team
    :parma tid: the team id to edit or create. If none, indicates a new team
    '''
    team = get_team(tid)

    # Need to create annotation counts with "total" for all members
    annotation_counts = summarize_team_annotations(team.members.all())
    edit_permission = has_team_edit_permission(request,team)

    context = {"team": team,
               "edit_permission":edit_permission,
               "annotation_counts":annotation_counts}

    # If the user has generated an invitation code
    if code is not None:
        context['code'] = code

    return render(request, "teams/team_details.html", context)


##################################################################################
# TEAM REQUESTS ##################################################################
##################################################################################


@login_required
def join_team(request, tid, code=None):
    '''add a user to a new team, and remove from previous team
    :parma tid: the team id to edit or create. If none, indicates a new team
    :param code: if the user is accessing an invite link, the code is checked
    against the generated request.
    '''
    team = get_team(tid)
    user = request.user
    add_user = True

    if team.permission == "institution":
        if not has_same_institution(request.user,team.owner):
            add_user = False
            # A user can be invited from a different institution
            if code is not None:
                add_user = is_invite_valid(team, code)
                if add_user == False:
                    messages.info(request, "You are not from the same institution, and this code is invalid to join.")
            else:
                messages.info(request,'''This team is only open to users in the team owner's institution.
                                         If you have an email associated with the institution, use the SAML institution
                                         log in.''')
            
    elif team.permission == "invite":
        if code is None:
            messages.info(request,"This is not a valid invitation to join this team.")
            add_user = False
        else:    
            add_user = is_invite_valid(team, code)
            if add_user == False:
                messages.info(request, "This code is invalid to join this team.")

    if add_user:   
        if user not in team.members.all():
            team.members.add(user)
            team.save()
            messages.info(request,"You have been added to team %s" %(team.name))
        else:
            messages.info(request,"You are already a member of %s!" %(team.name))

    return HttpResponseRedirect(team.get_absolute_url())


def add_collections(request,tid):
    team = get_team(tid)
    if request.method == "POST":
        if request.user == team.owner:
            collection_ids = request.POST.getlist("collection_ids",None)
            if collection_ids is not None:
                for collection_id in collection_ids:
                    team.add_collection(collection_id)
                team.save()
                messages.info(request,"%s collections added to team!" %(len(collection_ids)))
        else:
            messages.info(request, "Only team owners can edit teams.")
            return HttpResponseRedirect(team.get_absolute_url())

    context = {"team": team}
    return render(request, "teams/add_team_collections.html", context)


##################################################################################
# TEAM ACTIONS ###################################################################
##################################################################################

# Membership

@login_required
def request_membership(request,tid):
    '''generate an invitation for a user, return to view
    '''
    team = get_team(tid)
    if request.user not in team.members.all():
        old_request = get_request(user=request.user,team=team)
        if old_request is not None:
            message = "You already have a request to join team %s with status %s" %(team.name,
                                                                                    old_request.status)
        else:
            new_request = MembershipRequest.objects.create(team=team,
                                                           user=request.user)
            new_request.save()
            message = "Your request to join %s has been submit." %(team.name)

    else:
        message = "You are already a member of this team."
    return JsonResponse({"message":message})


@login_required
def leave_team(request,tid):
    team = get_team(tid)
    if request.user in team.members.all():
        team.members.remove(member)
        team.save()        
        message = "You has been removed from %s" %(team.name)
    else:
        message = "You are not a part of %s" %(team.name)
    return redirect('teams')


@login_required
def remove_member(request,tid,uid):
    team = get_team(tid)
    member = get_user(uid)
    if request.user == team.owner:
        if member in team.members.all():
            team.members.remove(member)
            team.save()        
            message = "%s has been removed from the team" %member.username
        else:
            message = "%s is not a part of this team." %member.username
    else:
        message = "You are not allowed to perform this action."
    return JsonResponse({"message":message})


@login_required
def generate_team_invite(request,tid):
    '''generate an invitation for a user, return to view
    '''
    team = get_team(tid)
    if request.user == team.owner:
        code = uuid.uuid4()
        new_invite = MembershipInvite.objects.create(team=team,
                                                     code=code)
        new_invite.save()
        return view_team(request, team.id, code=code)

    messages.info(request,"You do not have permission to invite to this team.")
    return HttpResponseRedirect(team.get_absolute_url())
