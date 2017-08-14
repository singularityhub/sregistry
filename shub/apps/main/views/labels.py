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

from shub.apps.main.models import (
    Container, 
    Collection,
    Label,
    Star
)

from django.shortcuts import (
    get_object_or_404, 
    render_to_response, 
    render, 
    redirect
)

from django.db.models import Q
from django.http import JsonResponse
from django.http.response import Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

import os
import re
import uuid

from .collections import get_collection




#### GETS #############################################################

def get_label(key=None,value=None):

    keyargs = dict()
    if key is not None:
        keyargs['key'] = key
    if value is not None:
        keyargs['value'] = value

    try:
        label = Label.objects.get(**keyargs)
    except Label.DoesNotExist:
        raise Http404
    else:
        return label



def all_labels(request):
    labels = Label.objects.all()
    context = {"labels":labels}
    return render(request, 'labels/all_labels.html', context)


# View containers for a tag
def view_label(request,lid):
    try:
        label = Label.objects.get(id=lid)
    except:
        messages.info(request,"This label does not exist.")
        return redirect('all_labels')

    context = {"label":label }

    return render(request, 'labels/view_label.html', context)


def update_container_labels(container,labels):
    for name,value in labels.items():
        label,created = Label.objects.get_or_create(key=name.lower(),
                                                    value=value.lower())

        label.save()
        
        # Does the container have the label with a different value?
        oldies = Label.objects.filter(
                         Q(containers=container) &
                         Q(key=name.lower)).exclude(value=value.lower())

        for oldie in oldies:
            oldie.containers.remove(container)
            oldie.save()

        if container not in label.containers.all():
            label.containers.add(container)
        container.save()
    return container
