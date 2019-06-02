'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from django.shortcuts import render
 


def index_view(request):
    return render(request, 'main/index.html')

def about_view(request):
    return render(request, 'main/about.html')

def tools_view(request):
    return render(request, 'main/tools.html')

def terms_view(request):
    return render(request, 'terms/usage_agreement.html')

