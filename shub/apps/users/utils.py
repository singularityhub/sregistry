'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017 Vanessa Sochat.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from rest_framework.authtoken.models import Token

def get_usertoken(user):
    try:
        token = Token.objects.get(user=user)
    except TokenDoesNotExist:
        token = Token.objects.create(user=user)
    return token.key
