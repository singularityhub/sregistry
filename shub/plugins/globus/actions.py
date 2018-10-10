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


from shub.apps.users.models import User
from django.contrib.auth.decorators import login_required
from social_django.models import UserSocialAuth
from shub.plugins.globus.utils import (
    get_client,
    get_transfer_client
)
from django.conf import settings
import requests
import globus_sdk


def get_endpoints(user, client=None):
    '''use a transfer client to list endpoints for the logged in user
    ''' 
    endpoints = []
    if client is None:
        client = get_transfer_client(user)
    if client is not None:
        for scope in ['my-endpoints', 'shared-with-me']:
            for ep in client.endpoint_search(filter_scope=scope):
                if ep.__dict__['_data']['name'] != settings.PLUGIN_GLOBUS_ENDPOINT:
                    endpoints.append(ep.__dict__['_data'])
    return endpoints


def search_endpoints(term, user, client=None):
    '''use a transfer client to search endpoints based on a terms
    ''' 
    endpoints = []
    if client is None:
        client = get_transfer_client(user)

    if client is not None:
        for ep in client.endpoint_search(term, filter_scope="all"):
            if ep.__dict__['_data']['name'] != settings.PLUGIN_GLOBUS_ENDPOINT:
                endpoints.append(ep.__dict__['_data'])

    return endpoints



def do_transfer(user, endpoint, container):

    # Use relative paths, we are in container and endpoint is mapped
    source = container.get_image_path()    
    client = get_transfer_client(user)
    source_endpoint = settings.PLUGIN_GLOBUS_ENDPOINT
    tdata = globus_sdk.TransferData(client, source_endpoint,
                                    endpoint,
                                    label="Singularity Registry Transfer",
                                    sync_level="checksum")
    tdata.add_item(source.replace(settings.MEDIA_ROOT,'/code/images'), 
                   source.replace(settings.MEDIA_ROOT,'').strip('/'))
    transfer_result = client.submit_transfer(tdata)
    return transfer_result
