'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017 Vanessa Sochat.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from shub.apps.users.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect


@login_required
def view_token(request):
    if request.user.is_superuser or request.user.admin is True:
        return render(request, 'users/token.html')
    else:
        messages.info(request,"You are not allowed to perform this action.")
        return redirect('collections')
