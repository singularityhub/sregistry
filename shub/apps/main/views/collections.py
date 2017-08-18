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

from singularity.utils import read_file
from shub.apps.users.views import validate_credentials
from django.shortcuts import (
    render, 
    redirect
)
from django.http.response import Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

import os
import re
import uuid


### AUTHENTICATION ####################################################


# get build collection
def get_collection(cid):
    keyargs = {'id':cid}
    try:
        collection = Collection.objects.get(**keyargs)
    except Collection.DoesNotExist:
        raise Http404
    else:
        return collection


###############################################################################################
# COLLECTIONS #################################################################################
###############################################################################################

# All container collections
def all_collections(request):
    collections = Collection.objects.filter(private=False)

    # Get information about if they have storage, and repo access
    context = validate_credentials(user=request.user)
    context["collections"] = collections
    context['page_title'] = "Container Collections"

    return render(request, 'collections/all_collections.html', context)


def user_collections(request,uid):
    '''this view will provide a list of user collections.
    '''
    try:
        user = User.objects.get(id=uid)
    except:
        messages.info(request,"This user does not exist.")
        return redirect('collections')

        
    collections = Collection.objects.filter(private=False,
                                            owner=user)

    # Get information about if they have storage, and repo access
    context = validate_credentials(user=request.user)
    context["collections"] = collections
    context['page_title'] = "User %s Collections" %user.username
    return render(request, 'collections/all_collections.html', context)



# Personal collections
@login_required
def my_collections(request):
    collections = Collection.objects.filter(owner=request.user)

    # Get information about if they have storage, and repo access
    context = validate_credentials(user=request.user)
    context["collections"] = collections
    context["page_title"] = "My Container Collections"
    return render(request, 'collections/all_collections.html', context)


# View container build details (all container builds for a repo)
def view_collection(request,cid):
    collection = get_collection(cid)

    # If private, and not the owner, no go.
    if collection.private == True and request.user != collection.owner:
        messages.info(request,"This collection is private.")
        return redirect('collections')

    # If the user is logged in, see if there is a star
    has_star = collection.has_collection_star(request)
    
    containers = collection.containers.all()
    edit_permission = collection.has_edit_permission(request)
    context = {"collection":collection,
               "containers":containers,
               "edit_permission":edit_permission,
               "star":has_star }
    return render(request, 'collections/view_collection.html', context)


# Edit a build for a collection
def edit_collection(request,cid):
    '''edit collection will let the user specify a different image for
    their builds, in the case that the provided isn't large enough, etc.
    :param cid: the id of the collection
    '''
    collection = get_collection(cid)

    edit_permission = collection.has_edit_permission(request)
    if not edit_permission:
        messages.info(request,"You are not permitted to perform this action.")
        return redirect('collections')
               
    if request.method == "POST":

        # Make private?
        private = request.POST.get("private", None)
        try:
            if private != None:
                if private == "True" and collection.private == False:
                    collection.private = True
                    messages.info(request,"The collection is now private.")
                    collection.save()
                elif private == "False" and collection.private == True:
                    collection.private = False
                    collection.save()
                    messages.info(request,"The collection is now public to share.")
        except:
            pass

    context = {'collection':collection,
               'edit_permission':edit_permission }

    return render(request, 'collections/edit_collection.html', context)


def collection_commands(request,cid):
    collection = get_collection(cid)

    # If private, and not the owner, no go.
    if collection.private == True and request.user != collection.owner:
        messages.info(request,"This collection is private.")
        return redirect('collections')

    context = {"collection":collection}
    return render(request, 'collections/collection_commands.html', context)


# Look only at container log
def delete_collection(request,cid):
    '''delete a container collection, including all containers and corresponding files.
    '''
    collection = get_collection(cid)

    if request.user != collection.owner:
        messages.info(request,"This action is not permitted.")
        return redirect('collections')

    # Delete files before containers
    containers = Container.objects.filter(collection=collection)
    
    for container in containers:
        container.delete()
    collection.delete()

    messages.info(request,'Collection successfully deleted.')
    return redirect('collections')






#######################################################################################
# COLLECTION PRIVACY / ACTIVE
#######################################################################################


@login_required
def change_collection_privacy(request,cid,make_private=True):
    '''change collection private is a wrapped for making a collection
    public or private.
    :param cid: the collection id to make private/public
    :param make_private: make the collection private (or not)
    '''
    collection = get_collection(cid)
    edit_permission = collection.has_edit_permission(request)

    # Customize message based on making public or private
    status = "private"
    if make_private == False:
        status = "public"

    # If the user has edit permission, make the repo private
    if edit_permission == True:

        # Making collection private must do check
        if make_private == True:
            collection.private = make_private 
            collection.save()
            messages.info(request,"Collection set to %s." %(status))
        else:
            collection.private = make_private    
            messages.info(request,"Collection set to %s." %(status))
            collection.save()

    else:
        messages.info(request,"You do not have permissions to perform this operation.")
    return redirect('collection_details', cid=collection.id)




@login_required
def make_collection_private(request,cid):
    '''make collection private will make a collection private
    :param cid: the collection id to make private
    '''
    return change_collection_privacy(request,cid,make_private=True)


@login_required
def make_collection_public(request,cid):
    '''make collection public will make a collection public
    :param cid: the collection id to make private
    '''
    return change_collection_privacy(request,cid,make_private=False)

