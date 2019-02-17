'''

Copyright (C) 2017-2018 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from shub.logger import bot
from sregistry.main.registry.auth import generate_timestamp
from shub.apps.api.utils import validate_request


def delete_container(request, container):
    '''delete a container only given authentication to do so'''

    auth=request.META.get('HTTP_AUTHORIZATION', None)

    if auth is None:
        bot.debug("authentication is invalid.")
        return False        

    timestamp = generate_timestamp()
    payload = "delete|%s|%s|%s|%s|" %(container.collection.name,
                                      timestamp,
                                      container.name,
                                      container.tag)
    bot.debug("Request payload %s" %payload)

    if not validate_request(auth,payload,"delete",timestamp):
        bot.debug("request is invalid.")
        return False

    return True
