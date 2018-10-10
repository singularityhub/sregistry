'''

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

from shub.apps.main.models import (
    Container, 
    Collection
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

from .containers import get_container




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

    containers = Container.objects.filter(tags__name=tag,
                                          collection__private=False)
    context = {"containers":containers,
               "tag":tag }

    return render(request, 'tags/view_tag.html', context)


#######################################################################################
# COLLECTION TAG MANAGEMENT
#######################################################################################

@login_required
def add_tag(request,cid):
    '''manually add a tag to the collection
    '''
    container = get_container(cid)
    edit_permission = container.collection.has_edit_permission(request)

    if edit_permission and request.method == "POST":
        tag = request.POST.get("tag",None)
        if tag is not None:
            container.tags.add(tag.lower())
            container.save()
            message = "Tag %s added to container." %(tag)
    else:
        message = "You do not have permissions to perform this operation."
    return JsonResponse({"message":message})



@login_required
def remove_tag(request,cid):
    '''remove a tag from a collection
    '''
    container = get_container(cid)
    edit_permission = container.collection.has_edit_permission(request)

    if edit_permission and request.method == "POST":
        tag = request.POST.get("tag", None)
        if tag is not None:
            tags = [x for x in container.tags.all() if x.name==tag.lower()]
            if len(tags) > 0:
                container.tags.remove(tag)
                container.save()

                # Check if remaining containers have tag
                tag = Tag.objects.get(name=tag.lower())
                if Container.objects.filter(tags__name=tag.lower()).count() == 0:
                    tag.delete()

                message = "Tag %s removed from continer." %(tag)
            else:
                message = "This tag is not present for this container"  
    else:
        message = "You do not have permissions to perform this operation."
    return JsonResponse({"message":message})
