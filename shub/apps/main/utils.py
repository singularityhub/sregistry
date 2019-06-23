'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from datetime import timedelta
from django.conf import settings
from django.utils import timezone

from sregistry.utils import read_json

import os
import re
import tempfile


def get_nightly_comparisons(date=None):
    '''load the latest nightly comparisons.

       Parameters
       ==========
       date: if provided, will load specified date instead of latest.
    '''
    root = os.path.abspath(os.path.join(settings.MEDIA_ROOT, 'trees', 'nightly'))
    base_name = "%s/container-tree" % root
    if date is None:
        date = "latest"
    base_name = "%s-%s.json" %(base_name, date)
    if os.path.exists(base_name):
        return read_json(base_name)
    return None


def write_tmpfile(memory_file):
    '''save tmp will extract a file to a temporary location
    '''
    tmpdir = tempfile.mkdtemp()
    file_name = '%s/%s' %(tmpdir, memory_file.name)
    with open(file_name, 'wb+') as dest:
        for chunk in memory_file.chunks():
            dest.write(chunk)
    return file_name


def format_collection_name(collection_name):
    '''remove illegal characters and ensure all lowercase'''
    collection_name = re.sub('[^0-9a-zA-Z]+', '-', collection_name)
    return collection_name.strip('-').lower()


def format_container_name(name, special_characters=None):
    '''format_container_name will take a name supplied by the user,
       remove all special characters (except for those defined by "special-characters"
       and return the new image name.
    '''
    if special_characters is None:
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
