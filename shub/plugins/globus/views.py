'''

Copyright (C) 2017-2019 Vanessa Sochat.

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
from .actions import ( 
    get_endpoints, 
    do_transfer, 
    search_endpoints
)
from .decorators import has_globus_association
from shub.plugins.globus.utils import (
    get_client, 
    get_transfer_client,
    associate_user
)

from globus_sdk.exc import TransferAPIError



@login_required
@has_globus_association
def globus_logout(request):
    '''log the user out of globus - this is a complete disconnect meaning
       that we revoke tokens and delete the social auth object.
    '''
    client = get_client()

    try:

        # Properly revoke and log out
        social = request.user.social_auth.get(provider="globus")
        for resource, token_info in social.extra_data.items(): 
            for token, token_type in token_info.items():
                client.oauth2_revoke_token(
                    token, additional_params={'token_type_hint': token_type})

        social.delete()

    except UserSocialAuth.DoesNotExist:
        pass

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

    redirect_uri = reverse('globus_login')
    # http://localhost/globus/login/"

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
def globus_transfer(request, cid=None, endpoints=None):
    ''' a main portal for working with globus. If the user has navigated
        here with a container id, it is presented with option to do a 
        transfer. If the method is a POST, we also do a custom search
        for a set of containers.
    '''
    container = None
    if cid is not None:
        container = get_container(cid)

    context = {'user': request.user,
               'container': container,
               'endpoint_search_term': "Search for..." }

    # Does the user want to search endpoints?

    if request.method == "POST":
        term = request.POST.get('term')
        if term is not None:
            endpoints = search_endpoints(term=term, user=request.user)
            context['endpoint_search_term'] = term.capitalize()

    # If we don't have any endpoints still

    if endpoints is None:
        endpoints = get_endpoints(request.user)

    context['endpoints'] = endpoints

    return render(request, 'globus/transfer.html', context)


@login_required
@has_globus_association
def globus_endpoint(request, endpoint_id=None, cid=None):
    ''' Show information for a single endpoint only.
    '''
    container = None
    if cid is not None:
        container = get_container(cid)

    context = {'user': request.user,
               'container': container,
               'endpoint_search_term': "Search for..." }

    # Get the endpoint
    try:
        client = get_transfer_client(request.user)
        endpoints =  [client.get_endpoint(endpoint_id).data]
    except TransferAPIError:
        endpoints = get_endpoints(request.user)

    context['endpoints'] = endpoints

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


        link = "https://globus.org/app/activity/%s" %result['task_id']
        m = result['message']
        m = "%s: <a target='_blank' href='%s'>view task</a>" %(m, link)

    status = {'message': m }
    return JsonResponse(status)
