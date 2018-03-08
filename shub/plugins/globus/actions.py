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
                if ep.__dict__['_data']['name'] != settings.GLOBUS_ENDPOINT_ID:
                    endpoints.append(ep.__dict__['_data'])
    return endpoints


def do_transfer(user, endpoint, container):

    # Use relative paths, we are in container and endpoint is mapped
    source = container.get_image_path().replace(settings.MEDIA_ROOT,'').strip('/')    
    client = get_transfer_client(user)
    source_endpoint = settings.GLOBUS_ENDPOINT_ID
    tdata = globus_sdk.TransferData(client, source_endpoint,
                                    endpoint,
                                    label="Singularity Registry Transfer",
                                    sync_level="checksum")
    tdata.add_item(source, source)
    transfer_result = client.submit_transfer(tdata)
    return transfer_result
