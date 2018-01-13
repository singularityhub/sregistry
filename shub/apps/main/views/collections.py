'''

Copyright (C) 2017-2018 The Board of Trustees of the Leland Stanford Junior
University.
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
from shub.settings import PRIVATE_ONLY
from itertools import chain

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

    # public collections
    collections = Collection.objects.filter(private=False)

    # private that the user can see
    private_collections = [x for x in Collection.objects.filter(private=True)
                           if x.has_edit_permission(request)]

    collections = list(chain(collections,private_collections))

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

        
    collections = Collection.objects.filter(owner=user)

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
    if collection.private == True and collection.has_edit_permission(request) == False:
        messages.info(request,"This collection is private.")
        return redirect('collections')

    # If the user is logged in, see if there is a star
    has_star = collection.has_collection_star(request)
    
    containers = collection.containers.all()
    edit_permission = collection.has_edit_permission(request)
    context = {"collection":collection,
               "containers":containers,
               "edit_permission":edit_permission,
               "star":has_star}
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
            if private != None and PRIVATE_ONLY is False:
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
    if PRIVATE_ONLY is True:
        messages.info(request,"This registry only allows private collections.")
        return redirect('collection_details', cid=cid)
    return change_collection_privacy(request,cid,make_private=False)

