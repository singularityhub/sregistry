'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

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
