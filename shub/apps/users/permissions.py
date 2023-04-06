"""

Copyright 2017-2023 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from shub.settings import USER_COLLECTION_LIMIT, USER_COLLECTIONS


def has_create_permission(request):
    """determine if a user can create a team.

    1. superusers and admin (global) can.
    2. If user collections is True, users can create teams
    """
    if request.user.is_superuser or request.user.is_staff:
        return True

    if USER_COLLECTIONS is True and not request.user.is_anonymous:
        # Does the registry have a user collection limit?
        if USER_COLLECTION_LIMIT is not None:
            if (
                request.user.container_collection_owners.count()
                >= USER_COLLECTION_LIMIT
            ):
                return False
        return True

    return False


def is_invite_valid(team, code):
    """determine if a user can be added to a team meaning
    he or she has an invite, and the invite corresponds to the
    code generated for it. a status (True or False)

    Parameters
    ==========
    team: the team to add to
    code: the code from the user

    """
    invitation = team.get_invite(code)

    # The invitation doesn't exist, period
    if invitation is None:
        return False

    # The invitation exists and is valid
    if invitation.code == code:
        return True
    return False
