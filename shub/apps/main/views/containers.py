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
    Label
)

from django.shortcuts import (
    render, 
    redirect
)

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib import messages
from datetime import datetime

import os
import json
import re



# get container
def get_container(cid):
    keyargs = {'id':cid}
    try:
        container = Container.objects.get(**keyargs)
    except Container.DoesNotExist:
        raise Http404
    else:
        return container



###############################################################################################
# HELPERS #####################################################################################
###############################################################################################

# View container, as a graphic
def view_container(request,cid):
    container = get_container(cid)

    if container.collection.private == True and request.user != container.collection.owner:
        messages.info(request,"This container is private.")
        return redirect('collections')

    messages.info(request,"We haven't decided what we want for this view yet! Do you have ideas?")
    return redirect('collection_details',cid=container.collection.id)


def view_named_container(request,collection,name,tag):
    '''view a specific container based on a collection, container, and tag name'''
    try:
        container = Container.objects.get(collection__name=collection,
                                          name=name,
                                          tag=tag)
    except Container.DoesNotExist:
        messages.info(request,"Container not found.")
        return redirect('collections')

    return container_details(request,container.id)


# Look at container spec,log,asciicast (details)
def container_details(request,cid):
    container = get_container(cid)

    if container.collection.private == True and request.user != container.collection.owner:
        messages.info(request,"This container is private.")
        return redirect('collections')

    edit_permission = container.has_edit_permission(request)
    labels = Label.objects.filter(containers=container)
    context = { "container":container,
                "labels":labels,
                "edit_permission": edit_permission }
    return render(request, 'containers/container_details.html', context)


# Look only at container log
def delete_container(request,cid):
    '''delete a container, including it's corresponding files, from google
    storage
    '''
    container = get_container(cid)
    collection = container.collection

    if request.user != collection.owner:
        messages.info(request,"This action is not permitted.")
        return redirect('collections')

    # Delete files and running instance, and container
    messages.info(request,'Container successfully deleted.')

    return redirect(collection.get_absolute_url())


# View container tags
def container_tags(request,cid):
    container = get_container(cid)

    if container.collection.private == True and request.user != container.collection.owner:
        messages.info(request,"This container is private.")
        return redirect('collections')

    context = {"container":container}
    return render(request, 'containers/container_tags.html', context)





###############################################################################################
# FREEZE ######################################################################################
###############################################################################################


@login_required
def change_freeze_status(request,cid):
    '''freeze or unfreeze a container
    :param cid: the container to freeze or unfreeze
    '''
    container = get_container(cid)
    edit_permission = container.has_edit_permission(request)

    if edit_permission == True:

        # If the container wasn't frozen, assign new version
        # '2017-08-06T19:28:43.294175'
        if container.version is None and container.frozen is False:
            container.version = datetime.now().isoformat()

        container.frozen = not container.frozen
        container.save()
        message = "Container %s:%s be overwritten by new pushes." %(container.name,
                                                                                        container.tag)
        if container.frozen: 
            message = "%s:%s is frozen, and will not be overwritten by push." %(container.name,
                                                                                container.tag)

        messages.info(request, message)
    else:
        messages.info(request,"You do not have permissions to perform this operation.")

    previous_page = request.META.get('HTTP_REFERER', None)
    if previous_page is not None:
        return HttpResponseRedirect(previous_page)

    return redirect('container_details', cid=container.id)
