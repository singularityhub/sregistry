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

from shub.apps.main.models import (
    Container, 
    Collection,
    Share,
    Star
)

from django.shortcuts import (
    get_object_or_404, 
    render_to_response, 
    render, 
    redirect
)

from django.http import (
    JsonResponse,
    HttpResponse,
    FileResponse
)

from shub.apps.main.utils import (
    calculate_expiration_date,
    validate_share
)

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http.response import Http404
from rest_framework import status
from rest_framework.response import Response

import os
import re
import uuid

from .containers import get_container



#######################################################################################
# CONTAINER DOWNLOAD
#######################################################################################

def download_recipe(request,cid):
    '''download a container recipe
    '''
    container = get_container(cid)
    if "deffile" in container.metadata:
        recipe = container.metadata['deffile']
        filename = "Singularity.%s" %container.tag

        response = HttpResponse(recipe,
                                content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="%s"' %filename
        return response


def download_share(request,cid,secret):
    '''download a custom share for a container
    '''
    container = get_container(cid)
    import pickle
    pickle.dump({'cid':cid,'secret':secret},open('days.pkl','wb'))

    # Is the container secret valid?
    try:
        share = Share.objects.get(secret=secret,
                                  container=container)
    except Share.DoesNotExist:
        raise Http404

    # If the share exists, ensure active
    if validate_share(share) is False:
        share.delete()
        raise Response(status.HTTP_403_FORBIDDEN)

    # Now validate the secret
    if secret != share.secret:
        raise Response(status.HTTP_401_UNAUTHORIZED)

    # If we make it here, link is good
    filename = container.get_download_name()

    f = open(container.image.get_abspath(), 'rb')
    response = FileResponse(f, content_type='application/img')
    response['Content-Disposition'] = 'attachment; filename="%s"' %filename
    
    return response



def download_container(request,cid,secret):
    '''download a container
    '''
    container = get_container(cid)

    # The secret must be up to date
    if container.secret != secret:
        return Http404

    filename = container.get_download_name()

    f = open(container.image.get_abspath(), 'rb')
    response = FileResponse(f, content_type='application/img')
    response['Content-Disposition'] = 'attachment; filename="%s"' %filename

    return response
