'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017 Vanessa Sochat.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

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
    HttpResponse
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
    response = HttpResponse(container.image.datafile.file,
                            content_type='application/img')
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
    response = HttpResponse(container.image.datafile.file,
                            content_type='application/img')
    response['Content-Disposition'] = 'attachment; filename="%s"' %filename
    return response
