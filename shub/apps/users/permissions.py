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

from shub.settings import USER_COLLECTIONS


def has_create_permission(request):
    ''' determine if a user can create a team.
  
        1. superusers and admin (global) can.
        2. If user collections is True, users can create teams
 
   '''
    if request.user.is_superuser or request.user.is_staff:
        return True
    if USER_COLLECTIONS is True and not request.user.is_anonymous:
        return True
    return False


def is_invite_valid(team, code):
    '''determine if a user can be added to a team meaning
       he or she has an invite, and the invite corresponds to the
       code generated for it. a status (True or False)

       Parameters
       ==========
       team: the team to add to
       code: the code from the user
       
    '''
    invitation = team.get_invite(code)
  
    # The invitation doesn't exist, period
    if invitation is None:
        return False

    # The invitation exists and is valid
    if invitation.code == code:
        return True
    return False
