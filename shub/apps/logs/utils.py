"""

Copyright (C) 2017-2022 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

import json
import re

from django.utils.timezone import now
from rest_framework.authtoken.models import Token


def get_request_collection(instance):
    """obtain the collection from a request

    Parameters
    ==========
    instance: should be an APIRequestLog object, with a response
              and path to parse
    """
    import pickle

    pickle.dump(instance, open("instance.pkl", "wb"))
    from shub.apps.main.models import Collection
    from sregistry.utils import parse_image_name

    try:
        response = json.loads(instance.response)
        name = response["collection"]
    except:

        # Case 1: library endpoint
        if "/v1/images" in instance.path:
            collection_name = instance.path.replace("/v1/images/", "")

        # Case 2: shub endpoint
        else:
            collection_name = instance.path.replace("/api/container/", "")
        name = parse_image_name(collection_name)["collection"]

    try:
        collection = Collection.objects.get(name=name)
    except Collection.DoesNotExist:
        collection = None

    return collection


def generate_log(
    view_name,
    ipaddr,
    remote_addr,
    params,
    request_path,
    host,
    request_data,
    auth_header,
    method,
):
    """a helper function to generate a log from a request, intended when
    we want the same functionality but not as a mixin.
    """
    from shub.apps.logs.models import APIRequestLog

    if ipaddr:
        # X_FORWARDED_FOR returns client1, proxy1, proxy2,...
        ipaddr = [x.strip() for x in ipaddr.split(",")][0]
    else:
        ipaddr = remote_addr

    request_method = method
    view_method = method.lower()

    # create log
    log = APIRequestLog(
        requested_at=now(),
        path=request_path,
        view=view_name,
        view_method=view_method,
        remote_addr=ipaddr,
        host=host,
        method=request_method,
        query_params=params,
    )

    # Get a user, if auth token is provided
    if auth_header:
        try:
            token = Token.objects.get(key=auth_header.replace("BEARER", "").strip())
            user = token.user
        except Token.DoesNotExist:
            pass

    log.user = user

    # get data dict
    try:
        log.data = clean_data(request_data.dict())
    except AttributeError:  # if already a dict, can't dictify
        log.data = clean_data(request_data)

    log.save()


def clean_data(data):
    """Clean a dictionary of data of potentially sensitive info before
    sending to the database.
    Function based on the "_clean_credentials" function of django
    (django/django/contrib/auth/__init__.py)
    """
    if data is None:
        return ""

    SENSITIVE_DATA = re.compile("api|token|key|secret|password|signature", re.I)
    CLEANSED_SUBSTITUTE = "********************"
    for key in data:
        if SENSITIVE_DATA.search(key):
            data[key] = CLEANSED_SUBSTITUTE
    return data
