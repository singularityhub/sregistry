'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017 Vanessa Sochat.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''


from shub.apps.main.models import Container
from singularity.utils import read_json
from shub.settings import MEDIA_ROOT

from itertools import chain
import os
import json
import re
import requests
import tempfile


def get_request_collection(instance):
    '''obtain the collection from a request

    Parameters
    ==========
    instance: should be an APIRequestLog object, with a response
              and path to parse
    '''
    from singularity.registry.utils import parse_image_name
    from shub.apps.main.models import Collection 
    
    try: 
        response = json.loads(instance.response)   
        name = response['collection']
    except:
        collection_name = instance.path.replace('/api/container/','')
        name = parse_image_name(collection_name)['collection']

    try:
        collection = Collection.objects.get(name=name)
    except Collection.DoesNotExist:
        collection = None

    return collection
