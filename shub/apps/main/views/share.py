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

from shub.apps.main.utils import calculate_expiration_date
from shub.apps.api.tasks import expire_share
from django.shortcuts import (
    render, 
    reverse
) 

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages
from datetime import datetime

from notifications.signals import notify
from shub.apps.users.utils import get_user

import os
import json
import re


@login_required
def generate_share(request, cid):
    '''generate a temporary share link for a container
    :param cid: the container to generate a share link for
    '''
    container = get_container(cid)
    edit_permission = container.has_edit_permission(request)

    if edit_permission == True:
        days = request.POST.get('days', None)
        if days is not None:    
            days = int(days)
            try:
                expire_date = calculate_expiration_date(days)
                share,created = Share.objects.get_or_create(container=container,
                                                            expire_date=expire_date)
                share.save()

                # Generate an expiration task
                expire_share.apply_async(kwargs={"sid": share.id}, 
                                         eta=expire_date)

                link = reverse('download_share', kwargs={'cid':container.id,
                                                         'secret':share.secret })

                expire_date = datetime.strftime(expire_date, '%b %m, %Y')
                response = {"status": "success",
                            "days": days,
                            "expire": expire_date,
                            "link": link }
            except:
                response = {"status": "error",
                            "days": days }

        return JsonResponse(response)

    return JsonResponse({"error":"You are not allowed to perform this action."})
