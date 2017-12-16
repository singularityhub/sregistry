'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017 Vanessa Sochat.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from django.shortcuts import render
 


def index_view(request):
    context = {}
    return render(request, 'main/index.html', context)

def about_view(request):
    context = {'active':'home'}
    return render(request, 'main/about.html', context)

def terms_view(request):
    context = {'active':'home'}
    return render(request, 'terms/usage_agreement.html', context)

