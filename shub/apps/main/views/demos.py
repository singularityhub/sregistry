'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017 Vanessa Sochat.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from django.shortcuts import (
    render, 
    redirect
)

from django.http.response import Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

import os
import re

from shub.apps.main.forms import DemoForm
from shub.apps.main.models import Demo



###############################################################################################
# DEMOS #######################################################################################
###############################################################################################


def get_demo(did):
    keyargs = {'id':did}
    try:
        demo = Demo.objects.get(**keyargs)
    except Demo.DoesNotExist:
        raise Http404
    else:
        return demo


def view_demo(request,did):
    demo = get_demo(did)
    context = {"collection":demo.collection,
               "demo":demo}
    return render(request, 'demos/view_demo.html', context)



def collection_demos(request,cid):
    from .collections import get_collection
    collection = get_collection(cid)
    demos = Demo.objects.filter(collection=collection)
    context = {"collection":collection,
               "demos":demos}
    return render(request, 'demos/collection_demos.html', context)



@login_required
def edit_demo(request,cid,did=None):
    '''view to edit/add a demo
    :param cid: the collection id, always required
    :param did: the demo id, not required
    '''
    from .collections import get_collection
    collection = get_collection(cid)
    context = {"collection": collection}

    # Is this a new demo, or updating a previous one?
    demo = Demo()
    if did is not None:
        demo = get_demo(did) 

    # Only let authenticated users make these changes
    if request.user.is_authenticated():
    
        if request.method == 'POST':
            form = DemoForm(request.POST)
            if form.is_valid():  
                demo = form.save(commit=False)
                demo.collection = collection
                if demo.kind == "ASCIINEMA":
                    demo = parse_asciinema(demo)
                demo.save()
                return redirect(demo) 
        else:
            form = DemoForm(instance=demo)
            context["form"] = form
            return render(request, 'demos/edit_demo.html', context)

    messages.info(request,"You must be authenticated to perform this action.")
    return redirect('container_collections')


###############################################################################################
# HELPERS #####################################################################################
###############################################################################################


def parse_asciinema(demo):
    '''if the user gives an asciinema url, parse it down to the id
    '''
    demo_id = demo.url
    if demo_id.startswith('http'):
        # If parameters supplied, remove them
        demo_id = demo_id.split('?')[0]
        if not demo_id.endswith('/'):
            demo_id = "%s/" %(demo_id)
        if demo_id.startswith('https'):
            demo_id = demo_id.replace('https','http')
        demo_id = demo_id.replace("http://asciinema.org/a/","")
        demo_id = demo_id.split('/')[0]
        demo.url = demo_id
    return demo
