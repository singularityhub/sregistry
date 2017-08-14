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
