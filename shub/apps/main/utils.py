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
