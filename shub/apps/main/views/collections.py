'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from shub.settings import (
    PRIVATE_ONLY,
    COLLECTIONS_VIEW_PAGE_COUNT as collection_count,
    VIEW_RATE_LIMIT as rl_rate, 
    VIEW_RATE_LIMIT_BLOCK as rl_block
)
from shub.apps.users.views import validate_credentials
from shub.apps.main.utils import format_collection_name
from shub.apps.main.models import (
    Container, 
    Collection
)


from django.shortcuts import (
    render, 
    redirect
)
from django.db.models import Q
from django.http.response import Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from itertools import chain
from ratelimit.decorators import ratelimit

import uuid


@ratelimit(key='ip', rate=rl_rate, block=rl_block)
def get_collection(cid):
    ''' get a collection based on its primary id, raise 404 not found
        if... not found :)

       Parameters
       ==========
       cid: the id of the collection to look up
   '''
    keyargs = {'id':cid}
    try:
        collection = Collection.objects.get(**keyargs)
    except Collection.DoesNotExist:
        raise Http404
    else:
        return collection

@ratelimit(key='ip', rate=rl_rate, block=rl_block)
def get_collection_named(name, retry=True):
    '''get a collection by name. First we try the collection name,
       then we try splitting if the name includes /

       Parameters
       ==========
       name: the name of the collection to look up
   '''
    try:
        collection = Collection.objects.get(name=name)
    except Collection.DoesNotExist:
        if retry is True and "/" in name:
            name = name.split('/')[0]
            return get_collection_named(name, retry=False)
        raise Http404
    else:
        return collection


################################################################################
# COLLECTIONS ##################################################################
################################################################################

@ratelimit(key='ip', rate=rl_rate, block=rl_block)
def all_collections(request):
    '''view all container collections. This only includes public collections,
       and we add collections for which the user has permission.

    '''
    limit = min(Collection.objects.count(), collection_count)
    collections = Collection.objects.filter(private=False).annotate(Count('star', distinct=True)).order_by('-star__count')[:limit]

    # private that the user can view
    private_collections = [x for x in Collection.objects.filter(private=True)
                           if x.has_view_permission(request)]

    collections = set(list(chain(collections, private_collections)))

    # Get information about if they have storage, and repo access
    context = validate_credentials(user=request.user)
    context["collections"] = collections

    return render(request, 'collections/all_collections.html', context)


@ratelimit(key='ip', rate=rl_rate, block=rl_block)
@login_required
def my_collections(request):
    '''this view will provide a list of collections for the logged in user
    '''
    user = request.user
    collections = Collection.objects.filter(Q(owners=user) | 
                                            Q(contributors=user)).distinct()

    # Get information about if they have storage, and repo access
    context = validate_credentials(user=request.user)
    context["collections"] = collections
    context["my_collections"] = True
    return render(request, 'collections/all_collections.html', context)


@ratelimit(key='ip', rate=rl_rate, block=rl_block)
@login_required
def new_collection(request):
    '''new_container_collection will display a form to generate a new collection
    '''
    if request.user.has_create_permission():
 
        if request.method == "POST":
            
            name = request.POST.get('name')
            if name is not None:

                # No special characters allowed
                name = format_collection_name(name)
                collection = Collection(name=name, secret=str(uuid.uuid4()))
                collection.save()
                collection.owners.add(request.user)
                collection.save()

            messages.info(request, 'Collection %s created.' % name)
            return redirect('collection_details', cid=collection.id)

        # Just new collection form, not a post
        else:
            return render(request, "collections/new_collection.html")

    # If user makes it down here, does not have permission
    messages.info(request, "You don't have permission to perform this action.")
    return redirect("collections")

@ratelimit(key='ip', rate=rl_rate, block=rl_block)
def view_named_collection(request, username, reponame):
    '''View container build details (all container builds for a repo)
       This is the same as view_collection but we look up the collection
       by its full name.

       Parameters
       ==========
       username: the owner of the collection
       reponame: the collection name
    '''
    # First attempt, try looking up collection by username/reponame
    try:
        collection = Collection.objects.get(name="%s/%s" %(username, reponame))
    except Collection.DoesNotExist:

        # Then look for username only
        try:
            collection = Collection.objects.get(name=username)
        except:
            raise Http404

    return _view_collection(request, collection)


def _view_collection(request, collection):
    '''a shared function to finish up checking permissions for viewing
       a collection, and returning to the user. Called by view_named_collection
       and view_collection
    '''
    edit_permission = collection.has_edit_permission(request)
    view_permission = collection.has_view_permission(request)

    # If private, and not the owner, no go.
    if collection.private and not view_permission:
        messages.info(request, "This collection is private.")
        return redirect('collections')

    # If the user is logged in, see if there is a star
    has_star = collection.has_collection_star(request)
    
    containers = collection.containers.all()
    context = {"collection":collection,
               "containers":containers,
               "edit_permission": edit_permission,
               "star":has_star}
    return render(request, 'collections/view_collection.html', context)


@ratelimit(key='ip', rate=rl_rate, block=rl_block)
def view_collection(request, cid):
    '''View container build details (all container builds for a repo)

       Parameters
       ==========
       cid: the collection id
 
    '''

    collection = get_collection(cid)
    return _view_collection(request, collection)


@ratelimit(key='ip', rate=rl_rate, block=rl_block)
def collection_settings(request, cid):
    '''Collection settings is the entrypoint for editing the builder, branches,
       and administrative actions like disabling and deleting collections. if 
       active tab is defined, it means we are coming from a submit to change one
       of these tabs, and it will return the user to the page with the correct
       tab active.
    
       Parameters
       ==========
       cid: the id of the collection
    '''
    from shub.apps.users.permissions import has_create_permission
    from shub.apps.users.models import Team

    collection = get_collection(cid)
    edit_permission = collection.has_edit_permission(request)
    has_create_permission = has_create_permission(request)

    # Give view a list of owner and member ids
    owners_ids = [x.id for x in collection.owners.all()]
    contrib_ids = [x.id for x in collection.contributors.all()]

    if request.user not in collection.owners.all():
        messages.info(request, "Only owners can change collection settings")
        return redirect('collection_details', cid=collection.id)

    if not edit_permission:
        messages.info(request, "You are not permitted to perform this action.")
        return redirect('collections')
               
    context = {'collection': collection,
               'teams': Team.objects.all(),
               'owners_ids': owners_ids,
               'contrib_ids': contrib_ids,
               'has_create_permission': has_create_permission,
               'edit_permission':edit_permission}

    return render(request, 'collections/collection_settings.html', context)


@ratelimit(key='ip', rate=rl_rate, block=rl_block)
def edit_collection(request, cid):
    '''edit collection will let the user specify a different image for
       their builds, in the case that the provided isn't large enough, etc.
   
       Parameters
       ==========
       cid: the id of the collection

    '''
    collection = get_collection(cid)

    edit_permission = collection.has_edit_permission(request)
    if not edit_permission:
        messages.info(request, "You are not permitted to perform this action.")
        return redirect('collections')
               
    if request.method == "POST":

        # Make private?
        private = request.POST.get("private")
        if private is not None and PRIVATE_ONLY is False:
            private = bool(private)

            # change is warranted
            if collection.private != private:
                collection = _change_collection_privacy(request=request,
                                                        collection=collection,
                                                        make_private=private)



    context = {'collection':collection,
               'edit_permission':edit_permission}

    return render(request, 'collections/edit_collection.html', context)

@ratelimit(key='ip', rate=rl_rate, block=rl_block)
def collection_commands(request, cid):
    '''collection commands will show the user example commands for interacting
       with a collection

       Parameters
       ==========
       cid: the collection id to view commands for

    '''

    collection = get_collection(cid)

    # If private, and not the owner, no go.
    if not collection.has_view_permission(request):
        messages.info(request, "This collection is private.")
        return redirect('collections')

    context = {"collection":collection}
    return render(request, 'collections/collection_commands.html', context)

@ratelimit(key='ip', rate=rl_rate, block=rl_block)
def delete_collection(request, cid):
    '''delete a container collection

       Parameters
       ==========
       cid: the collection id to delete

    '''
    if not _delete_collection(request, cid):
        messages.info(request, "This action is not permitted.")
        return redirect('collections')

    messages.info(request, 'Collection successfully deleted.')
    return redirect('collections')


def _delete_collection(request, cid):
    ''' the underlying call for delete_collection, intended for use
        also not directly from a view. Returns True or False if the
        collection is deleted.
    '''
    collection = get_collection(cid)

    # Only an owner can delete
    if not collection.has_edit_permission(request):
        return False

    # Delete files before containers
    containers = Container.objects.filter(collection=collection)
    
    for container in containers:
        container.delete()
    collection.delete()
    return True


################################################################################
# COLLECTION PRIVACY / ACTIVE
################################################################################

def _change_collection_privacy(request, collection, make_private=True):
    ''' the underlying driver for the view (and settings page) to change
        the privacy for a collection. We check the ownership and permission,
        make the change, and return the updated collection.

       Parameters
       ==========
       request: the request object with user permissions, etc.
       collection: the collection to make private
       make_private: boolean, True indicates asking for private
    '''
    edit_permission = collection.has_edit_permission(request)

    # Customize message based on making public or private
    status = "private"
    if not make_private:
        status = "public"

    # If the user has edit permission, make the repo private
    if edit_permission:
        collection.private = make_private 
        messages.info(request, "Collection set to %s." % status)
        collection.save()

    else:
        messages.info(request, "You need permissions to perform this operation.")
    return collection


@ratelimit(key='ip', rate=rl_rate, block=rl_block)
@login_required
def change_collection_privacy(request, cid, make_private=True):
    '''change collection privacy, if the user has permission

       Parameters
       ==========
       cid: the collection id to make private/public
       make_private: make the collection private (or not)

    '''
    collection = get_collection(cid)
    collection = _change_collection_privacy(request=request,
                                            collection=collection,
                                            make_private=make_private)

    return redirect('collection_details', cid=collection.id)



@ratelimit(key='ip', rate=rl_rate, block=rl_block)
@login_required
def make_collection_private(request, cid):
    '''make collection private will make a collection private

       Parameters
       ==========
       cid: the collection id to make private
    '''
    return change_collection_privacy(request, cid, make_private=True)


@ratelimit(key='ip', rate=rl_rate, block=rl_block)
@login_required
def make_collection_public(request, cid):
    '''make collection public will make a collection public

       Parameters
       ==========
       cid: the collection id to make public
    '''
    if PRIVATE_ONLY:
        messages.info(request, "This registry only allows private collections.")
        return redirect('collection_details', cid=cid)
    return change_collection_privacy(request, cid, make_private=False)


################################################################################
# Contributors #################################################################
################################################################################

def _edit_contributors(userids, collection, add_user=True, level="contributor"):
    '''a general function to add a single (or list) of users to a collection,
       given that each user exists.
 
       Parameters
       ==========
       userids: a string list, or single string of a user id
       add_user: if True, perform add on the collection. If False, remove.
       level: one of contributor or owner.
    '''
    from shub.apps.users.utils import get_user

    if not isinstance(userids, list):
        userids = [userids]

    for userid in userids:
        user = get_user(userid)

        if user is not None:

            # Are we adding an owner or a contributor?
            func = collection.owners
            if level == "contributor":
                func = collection.contributors

            # Are we adding or removing?
            if add_user is True:
                func.add(user)
            else:
                func.remove(user)
            collection.save()

    return collection

@ratelimit(key='ip', rate=rl_rate, block=rl_block)
@login_required
def edit_contributors(request, cid):
    '''edit_contributors is the submission to see, add, and delete contributors 
       for a collection. Only owners are allowed to do this, and can only
       see individuals in their teams.
    '''
    
    collection = get_collection(cid)

    # Who are current owners?
    owners = collection.owners.all()

    if request.user in owners:

        if request.method == "POST":

            # Add and remove owners and contributors
            unset = [None, "", []]
            add_contribs = request.POST.get('add_contributors')
            remove_contribs = request.POST.get('remove_contributors')
            add_owners = request.POST.get('add_owners')
            remove_owners = request.POST.get('remove_owners')

            if add_contribs not in unset:
                collection = _edit_contributors(userids=add_contribs, 
                                                collection=collection)
            if add_owners not in unset:
                collection = _edit_contributors(userids=add_owners, 
                                                collection=collection,
                                                level="owner")

            if remove_contribs not in unset:
                collection = _edit_contributors(userids=remove_contribs, 
                                                collection=collection,
                                                add_user=False)

            if remove_owners not in unset:

                # Do not allow all owners to be removed
                if len(remove_owners) < collection.owners.count():
                    collection = _edit_contributors(userids=remove_owners, 
                                                    collection=collection,
                                                     add_user=False,
                                                level="owner")
                else:
                    messages.info(request, "You must have at least one owner.")

    return redirect('collection_settings', cid=cid)
