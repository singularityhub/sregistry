'''

Copyright (C) 2017-2018 Vanessa Sochat.
Copyright (C) 2017-2018 The Board of Trustees of the Leland Stanford Junior
University.


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

from django.conf import settings
from shub.logger import bot
from shub.apps.main.views import get_container
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from .actions import get_endpoints, do_transfer
from .decorators import has_globus_association
from shub.plugins.globus.utils import (
    get_client, 
    associate_user
)

@login_required
@has_globus_association
def globus_logout(request):
    '''log the user out of globus, meaning deleting the association,
    and then revoking all tokens'''
    credentials = request.user.disconnect('globus')
    client = get_client()
    for resource, token_info in credentials.extra_data.items(): 
        for token, token_type in token_info.items():
            client.oauth2_revoke_token(
                token, additional_params={'token_type_hint': token_type})

    # Redirect to globus logout page?
    redirect_name = "Singularity Registry"
    redirect_url = "%s%s" %(settings.DOMAIN_NAME, reverse('profile'))
    logout_url = 'https://auth.globus.org/v2/web/logout'
    params = '?client=%s&redirect_uri=%s&redirect_name=%s' %(client.client_id,
                                                             redirect_url,
                                                             redirect_name)
    return redirect("%s%s" %(logout_url, params))


@login_required
def globus_login(request):
    '''
       Associate the logged in user with a globus account based on email.
       If the association doesn't exist, create it. Redirect to transfer
       page.
    '''

    # redirect_uri = reverse('globus_login')
    redirect_uri = "http://localhost/globus/login/"

    client = get_client()
    client.oauth2_start_flow(redirect_uri,
                             refresh_tokens=True)

    # First step of authentication flow - we need code
    if "code" not in request.GET:
        auth_uri = client.oauth2_get_authorize_url()
        return redirect(auth_uri)

    else:

        # Second step of authentication flow - we need to ask for token  
        code = request.GET.get('code')
        user = associate_user(request.user, 
                              client=client, 
                              code=code)

    return redirect('globus_transfer')


@login_required
@has_globus_association
def globus_transfer(request, cid=None):
    ''' a main portal for working with globus. If the user has navigated
        here with a container id, it is presented with option to do a 
        transfer
    '''
    container = None
    if cid is not None:
        container = get_container(cid)
    endpoints = get_endpoints(request.user)
    context = {'user': request.user,
               'endpoints': endpoints,
               'container': container }

    return render(request, 'globus/transfer.html', context)


@login_required
@has_globus_association
def submit_transfer(request, endpoint, cid):
    '''submit a transfer request for a container id to an endpoint, also
       based on id
    '''

    container = get_container(cid)
    if container is None:
        message = "This container could not be found."

    else:
        result = do_transfer(user=request.user,
                             endpoint=endpoint,
                             container=container)
        message = result['message']

    status = {'message': message }
    return JsonResponse(status)
