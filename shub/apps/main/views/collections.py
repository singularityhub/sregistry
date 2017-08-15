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

from shub.apps.main.utils import (
    get_collection_users,
    get_nightly_comparisons,
    get_container_log,
    write_tmpfile
)

from singularity.analysis.classify import estimate_os
from singularity.analysis.compare import (
    calculate_similarity,
    compare_containers
)

from singularity.utils import read_file
from singularity.views.trees import (
    container_tree,
    container_similarity,
    container_difference
)

from shub.apps.users.views import validate_credentials

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

        # Set the new padding
        padding = request.POST.get("padding",None)
        try:
            if padding != None:
                previous_padding = collection.build_padding
                collection.build_padding = int(padding)
                collection.save()
                if collection.build_padding != previous_padding:
                    messages.info(request,"Padding is set to %s" %padding)
        except:
            pass
            messages.info(request,"Padding %s is not valid, skipping save." %(padding)) 

        # Set the new size
        build_size = request.POST.get("build_size",None)
        try:
            if build_size != None:
                previous_size = collection.build_size
                if build_size != previous_size:
                    if build_size == '':
                        collection.build_size = None
                        messages.info(request,"Build size specification removed from build.")
                    else:
                        collection.build_size = int(build_size)
                        messages.info(request,"Build size is set to %s" %(build_size))
                    collection.save()
        except:
            pass
            messages.info(request,"Build size %s is not valid, skipping save." %(build_size))

        # Enable or disable debug
        build_debug = request.POST.get("build_debug",None)
        try:
            if build_debug != None:
                if build_debug == "True" and collection.build_debug == False:
                    collection.build_debug = True
                    messages.info(request,"Debug set to True.")
                    collection.save()
                elif build_debug == "False" and collection.build_debug == True:
                    collection.build_debug = False
                    collection.save()
                    messages.info(request,"Build debug set to False")
        except:
            pass

        # Build on deployment instead
        build_trigger = request.POST.get("build_trigger",None)
        if build_trigger is not None:
            try:           
                collection.build_trigger = build_trigger
                collection.save()
                if build_trigger == "DEPLOYMENT":
                    messages.info(request,"Build set to trigger on successful deployment testing status.")
                elif build_trigger == "COMMIT":
                    messages.info(request,"Build set to trigger on commits.")
            except:
                pass

        # Set the new builder
        new_builder = request.POST.get("builder_name",None) 
        if new_builder == None:
            messages.info(request,"Please specify a builder.")

        elif new_builder not in BUILDER_OPTIONS: 
            messages.info(request,"This is not a valid builder! Choices are %s" %(",".join(BUILDER_OPTIONS)))

        elif new_builder == current_selection:
            messages.info(request,"Builder %s is already selected for this collection." %(new_builder))

        else:       
            builder.specs['builder_name'] = new_builder
            builder.save()
            messages.info(request,"Builder changed from %s to %s. This builder will be used for new builds." %(current_selection,new_builder))
            current_selection = new_builder

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
def change_build_enabled(request,cid):
    '''change_build_enabled will change the build from enabled/disabled,
    or vice versa. This is the user's control for turning Github hooks on/off
    :param cid: the collection id to make private/public
    '''
    collection = get_collection(cid)
    edit_permission = collection.has_edit_permission(request)

    if edit_permission == True:
        collection.enabled = not collection.enabled
        collection.save()
        messages.info(request,"Collection enabled set to %s." %(collection.enabled))
    else:
        messages.info(request,"You do not have permissions to perform this operation.")
    return redirect('collection_details', cid=collection.id)


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

