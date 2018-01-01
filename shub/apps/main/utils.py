'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017 Vanessa Sochat.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from datetime import timedelta
from django.utils import timezone

from shub.apps.main.models import Container
from singularity.utils import read_json
from shub.settings import MEDIA_ROOT

from itertools import chain
import os
import re
import requests
import tempfile


def get_nightly_comparisons(date=None):
    '''load the latest nightly comparisons.
    :param date: if provided, will load specified date instead of latest.
    '''
    root = os.path.abspath(os.path.join(MEDIA_ROOT,'trees','nightly'))
    base_name = "%s/container-tree" %(root)
    if date == None:
        date = "latest"
    base_name = "%s-%s.json" %(base_name,date)
    if os.path.exists(base_name):
        return read_json(base_name)
    return None


def get_collection_users(collection):
    '''get_collection_users will return a list of all owners and contributors for
    a collection
    :param collection: the collection object to use
    '''
    contributors = collection.contributors.all()
    owner = collection.owner
    return list(chain(contributors,[owner]))


def write_tmpfile(memory_file):
    '''save tmp will extract a file to a temporary location
    '''
    tmpdir = tempfile.mkdtemp()
    file_name = '%s/%s' %(tmpdir,memory_file.name)
    with open(file_name, 'wb+') as dest:
        for chunk in memory_file.chunks():
            dest.write(chunk)
    return file_name


def format_container_name(name,special_characters=None):
    '''format_container_name will take a name supplied by the user,
    remove all special characters (except for those defined by "special-characters"
    and return the new image name.
    '''
    if special_characters == None:
        special_characters = []
    return ''.join(e.lower() for e in name if e.isalnum() or e in special_characters)


def validate_share(share):
    '''compare the share expiration date with the current date

    Parameters
    ==========
    share: a shub.apps.main.models.Share object, holding a container,
           and an expiration date.

    Returns
    =======
    True if valid, False if not. If False, will delete share.
    '''
    today = timezone.now()
    if today <= share.expire_date:
        return True
    return False


def calculate_expiration_date(days=7):
    '''calculate the expiration date of a share, in days,
    from the current time.'''
    today = timezone.now()
    return today + timedelta(days)
