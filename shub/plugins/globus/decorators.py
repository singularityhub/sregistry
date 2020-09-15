"""

Copyright (C) 2017-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.shortcuts import redirect
from django.contrib import messages


def has_globus_association(function):
    """ensure that a user has globus before continuing. If not, redirect
    to profile where the user can connect the account.
    """

    def wrap(request, *args, **kwargs):
        # Double check for Globus associated account
        if request.user.get_credentials("globus") is None:
            messages.info(
                request,
                "You must have an associated Globus account to perform this action.",
            )
            return redirect("profile")
        return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
