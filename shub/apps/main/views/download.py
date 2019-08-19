'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from django.contrib import messages
from django.http.response import Http404
from django.http import HttpResponseForbidden

from django.shortcuts import redirect

from django.http import (
    HttpResponse,
    FileResponse
)

from shub.apps.main.models import Share
from shub.apps.main.utils import validate_share
from shub.settings import (
    VIEW_RATE_LIMIT as rl_rate, 
    VIEW_RATE_LIMIT_BLOCK as rl_block,
    PLUGINS_ENABLED
)

from ratelimit.decorators import ratelimit
from rest_framework import status
from rest_framework.response import Response

import os

from .containers import get_container


################################################################################
# CONTAINER DOWNLOAD
################################################################################

@ratelimit(key='ip', rate=rl_rate, block=rl_block)
def download_recipe(request, cid):
    '''download a container recipe
    '''
    container = get_container(cid)

    if "deffile" in container.metadata:
        recipe = container.metadata['deffile']
        filename = "Singularity.%s" % container.tag

        response = HttpResponse(recipe,
                                content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="%s"' %filename
        return response

    messages.info(request, "Container does not have recipe locally.")
    return redirect(container.get_absolute_url())


@ratelimit(key='ip', rate=rl_rate, block=rl_block)
def download_share(request, cid, secret):
    '''download a custom share for a container
    '''
    container = get_container(cid)

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

    return _download_container(container, request)


@ratelimit(key='ip', rate=rl_rate, block=rl_block)
def download_container(request, cid, secret):
    '''download a container
    '''
    container = get_container(cid)

    # The secret must be up to date
    if container.collection.secret != secret:
        raise Http404

    return _download_container(container, request)


def _download_container(container, request):
    '''
       download_container is the shared function between downloading a share
       or a direct container download. For each, we create a FileResponse
       with content type application/img, and stream it to the container's
       download name. A FileResponse is returned.

       Parameters
       ==========
       container: the container to download

    '''
    if container.image is not None:

        filename = container.get_download_name()
        filepath = container.image.get_abspath()

        f = open(filepath, 'rb')
        response = FileResponse(f, content_type='application/img')
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        response['Content-Length'] = os.path.getsize(filepath)

        # Add 1 to the get count
        if container.get_count < container.get_limit:
            container.get_count += 1
            container.collection.get_count += 1
            container.collection.save()
            container.save()
            return response

        return HttpResponseForbidden()

  
    # A remove build will store a metadata image url
    elif 'image' in container.metadata:
         
        if "google_build" in PLUGINS_ENABLED:
            from shub.plugins.google_build.utils import generate_signed_url
            signed_url = generate_signed_url(container.metadata['image'])

            # If we can generate a URL, add one to limit and return url
            if signed_url != None and container.get_count < container.get_limit:
                container.get_count += 1
                container.collection.get_count += 1
                container.collection.save()
                container.save()
                return redirect(signed_url)
            return HttpResponseForbidden()

        # There is no container
        raise Http404

    else:
        raise Http404
