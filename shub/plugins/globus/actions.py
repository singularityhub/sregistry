"""

Copyright (C) 2017-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""


from django.conf import settings
from shub.plugins.globus.utils import get_transfer_client
import globus_sdk


def get_endpoints(user, client=None):
    """use a transfer client to list endpoints for the logged in user"""
    endpoints = []
    if client is None:
        client = get_transfer_client(user)
    if client is not None:
        for scope in ["my-endpoints", "shared-with-me"]:
            for ep in client.endpoint_search(filter_scope=scope):
                if ep.__dict__["_data"]["name"] != settings.PLUGIN_GLOBUS_ENDPOINT:
                    endpoints.append(ep.__dict__["_data"])
    return endpoints


def search_endpoints(term, user, client=None):
    """use a transfer client to search endpoints based on a terms"""
    endpoints = []
    if client is None:
        client = get_transfer_client(user)

    if client is not None:
        for ep in client.endpoint_search(term, filter_scope="all"):
            if ep.__dict__["_data"]["name"] != settings.PLUGIN_GLOBUS_ENDPOINT:
                endpoints.append(ep.__dict__["_data"])

    return endpoints


def do_transfer(user, endpoint, container):

    # Use relative paths, we are in container and endpoint is mapped
    source = container.get_image_path()
    client = get_transfer_client(user)
    source_endpoint = settings.PLUGIN_GLOBUS_ENDPOINT
    tdata = globus_sdk.TransferData(
        client,
        source_endpoint,
        endpoint,
        label="Singularity Registry Transfer",
        sync_level="checksum",
    )
    tdata.add_item(
        source.replace(settings.MEDIA_ROOT, "/code/images"),
        source.replace(settings.MEDIA_ROOT, "").strip("/"),
    )
    transfer_result = client.submit_transfer(tdata)
    return transfer_result
