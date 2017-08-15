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
    Star
)

from taggit.models import Tag

from django.shortcuts import (
    get_object_or_404, 
    render_to_response, 
    render, 
    redirect
)

from django.http import JsonResponse
from django.http.response import Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

import os
import re
import uuid

from .collections import get_collection




#### GETS #############################################################

def get_tag(name=None,tid=None):

    keyargs = dict()
    if name is not None:
        keyargs['name'] = name
    if tid is not None:
        keyargs['id'] = tid

    try:
        tag = Tag.objects.get(**keyargs)
    except Tag.DoesNotExist:
        raise Http404
    else:
        return tag


###############################################################################################
# TAGS ########################################################################################
###############################################################################################


def all_tags(request):
    tags = Tag.objects.all()
    context = {"tags":tags}
    return render(request, 'tags/all_tags.html', context)


# View containers for a tag
def view_tag(request,tid):
    try:
        tag = Tag.objects.get(id=tid)
    except:
        messages.info(request,"This tag does not exist.")
        return redirect('all_tags')

    collections = Collection.objects.filter(tags__name=tag,
                                            private=False)
    context = {"collections":collections,
               "tag":tag }

    return render(request, 'tags/view_tag.html', context)


#######################################################################################
# COLLECTION TAG MANAGEMENT
#######################################################################################

@login_required
def add_tag(request,cid):
    '''manually add a tag to the collection
    '''
    collection = get_collection(cid)
    edit_permission = collection.has_edit_permission(request)

    if edit_permission and request.method == "POST":
        tag = request.POST.get("tag",None)
        if tag is not None:
            collection.tags.add(tag.lower())
            collection.save()
            message = "Tag %s added to collection." %(tag)
    else:
        message = "You do not have permissions to perform this operation."
    return JsonResponse({"message":message})


@login_required
def remove_tag(request,cid):
    '''remove a tag from a collection
    '''
    collection = get_collection(cid)
    edit_permission = collection.has_edit_permission(request)

    if edit_permission and request.method == "POST":
        tag = request.POST.get("tag",None)
        if tag is not None:
            tags = [x for x in collection.tags.all() if x.name==tag.lower()]
            if len(tags) > 0:
                collection.tags.remove(tag)
                collection.save()
                message = "Tag %s removed from collection." %(tag)
            else:
                message = "This tag is not present in this collection."    
    else:
        message = "You do not have permissions to perform this operation."
    return JsonResponse({"message":message})
