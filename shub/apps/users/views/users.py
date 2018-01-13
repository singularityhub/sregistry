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
