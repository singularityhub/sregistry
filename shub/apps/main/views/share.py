'''

Copyright (c) 2017, Vanessa Sochat, All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''

from shub.apps.main.models import (
    Container,
    Label,
    Share
)

from shub.apps.main.utils import calculate_expiration_date
from shub.apps.api.tasks import expire_share
from django.shortcuts import (
    render, 
    reverse,
    redirect
)

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages
from datetime import datetime

import os
import json
import re

from .containers import get_container


@login_required
def generate_share(request,cid):
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
