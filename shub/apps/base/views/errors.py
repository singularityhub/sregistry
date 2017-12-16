'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017 Vanessa Sochat.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from django.shortcuts import render
from django.template.context import RequestContext


def handler404(request):
    response = render(request,'base/404.html', {})
    response.status_code = 404
    return response

def handler500(request):
    response = render(request,'base/500.html', {})
    response.status_code = 500
    return response
