'''

Copyright (C) 2017-2018 The Board of Trustees of the Leland Stanford Junior
University.
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

from django.http import JsonResponse
from shub.logger import bot

from rest_framework.permissions import (
    DjangoObjectPermissions,
    SAFE_METHODS, 
    Http404
)

from sregistry.utils import write_file
from shub.apps.users.models import User
from shub.settings import USER_COLLECTIONS

from datetime import datetime, timezone
import hashlib
import hmac
import base64
import json
import requests
import shutil
import tempfile
import re



def _parse_header(auth):
    '''parse a header and check for the correct digest.

       Parameters
       ==========
       auth: the challenge from the header      
    '''

    header,content = auth.split(' ')
    content = content.split(',')
    values = dict()
    for entry in content:
         key,val = re.split('=', entry, 1)
         values[key] = val

    values['header'] = header
    return values
        

def get_request_user(auth):
    '''get the user for the request from an authorization object
    '''
    user = None
    values = _parse_header(auth)

    if "Credential" not in values:
        bot.debug('Headers missing, request is invalid.')
        return user

    kind,username,ts = values['Credential'].split('/')
    username = base64.b64decode(username)

    try:
        user = User.objects.get(username=username)
    except:
        bot.debug('%s is not a valid user, request invalid.' %username)
    return user


def has_permission(auth, instance=None, pull_permission=True):
    '''a simple function to parse an authentication challenge for the username,
       and determine if the user has permission to perform the action.
     
       Parameters
       ==========
       auth: the challenge from the header
       instance: the instance to check for
       permission: the permission needed
       pull_permission: if True, the user is asking to pull. If False, push

    '''
    values = _parse_header(auth)

    if "Credential" not in values:
        bot.debug('Headers missing, request is invalid.')
        return False

    kind,username,ts = values['Credential'].split('/')
    username = base64.b64decode(username)

    try:
        user = User.objects.get(username=username)
    except:
        bot.debug('%s is not a valid user, request invalid.' %username)
        return False

    # A new collection, created by user or staff
    if user.is_superuser or user.is_staff:
        return True

    # An existing collection for a user with permission

    if instance is not None:

        # Asking to pull
        if pull_permission is True:
            return instance.has_view_permission(user)

        # Asking to push
        else:

            # Are users allowed?
            if USER_COLLECTIONS is False:
                return False

            return instance.has_edit_permission(user)

    return False




def validate_request(auth,
                     payload,
                     sender="push",
                     timestamp=None,
                     superuser=True):

    '''validate header and payload for a request

    Parameters
    ==========
    auth: the Authorization header content
    payload: the payload to assess
    timestamp: the timestamp associated with the request
    superuser: if the user must be superuser for validity

    Returns
    =======
    True if the request is valid, False if not

    '''
    values = _parse_header(auth)

    if values['header'] != 'SREGISTRY-HMAC-SHA256':
        bot.debug('Invalid SREGISTRY Authentication scheme, request invalid.')
        return False

    if "Credential" not in values or "Signature" not in values:
        bot.debug('Headers missing, request is invalid.')
        return False

    kind,username,ts = values['Credential'].split('/')
    username = base64.b64decode(username)
    if kind != sender:
        bot.debug('Mismatch: type (%s) sender (%s) invalid.' %(kind,sender))
        return False

    if timestamp is not None:
        if ts != timestamp:
            bot.debug('%s is expired, must be %s.' %(ts,timestamp))
            return False

    try:
        user = User.objects.get(username=username)
    except:
        bot.debug('%s is not a valid user, request invalid.' %username)
        return False

    request_signature = values['Signature']
    secret = user.token()
    return validate_secret(secret,payload,request_signature)


def encode(item):
    ''' encode an item to bytes to work with hexdigest

    Parameters
    ==========
    item: some string or bytes value to check
    '''
    if not isinstance(item,bytes):
        item = item.encode('utf-8')
    return item


def validate_secret(secret,payload,request_signature):
    ''' use hmac digest to compare a request_signature to one generated
    using a server secret against a payload. Valid means matching.

    Parameters
    ==========
    secret: the secret to generate the hash
    payload: the content to include in the digest
    request_signature: the signature generated by the request
                       to check against

    Returns
    =======
    True if secret + payload to generate signature matches 
                       request signature

    '''
    payload = encode(payload)
    request_signature = encode(request_signature)
    secret = encode(secret)
    digest = hmac.new(secret,digestmod=hashlib.sha256,
                      msg=payload).hexdigest().encode('utf-8')
    return hmac.compare_digest(digest, request_signature)



################################################################################
# PERMISSIONS
################################################################################


class ObjectOnlyPermissions(DjangoObjectPermissions):

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_authenticated()
        )

