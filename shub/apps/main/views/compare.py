'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from shub.apps.main.models import (
    Container, 
    Collection
)

from django.template import loader, Context
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import (
    render, 
    redirect
)

from django.contrib import messages
from itertools import chain

import datetime
import os
import json
import re
import shutil


###############################################################################################
# FILE SYSTEM USAGE ###########################################################################
###############################################################################################

def generate_size_data(collections, collection_level):
    '''generate a datastructure that can be rendered as:
    id,value
    flare,
    flare.analytics,
    flare.analytics.cluster,
    flare.analytics.cluster.AgglomerativeCluster,3938,1
    flare.analytics.cluster.CommunityStructure,3812,2
    flare.analytics.cluster.HierarchicalCluster,6714,3
    flare.analytics.cluster.MergeEdge,743,4
    flare.analytics.graph,,5
    flare.analytics.graph.BetweennessCentrality,3534,6
    flare.analytics.graph.LinkDistance,5731,7
    flare.analytics.graph.MaxFlowMinCut,7840,8
    flare.analytics.graph.ShortestPaths,5914,9
    flare.analytics.graph.SpanningTree,3416,10
    '''
    data = dict()
    for collection in collections:
        if collection.name not in data:
            data[collection.name] = {}

        # Generate data on the level of containers
        if collection_level is False:
            containers = collection.containers.all()
            for container in containers:
                if container.name not in data[collection.name]:
                    data[collection.name][container.name] = dict()
                if 'size_mb' in container.metadata:
                    data[collection.name][container.name][container.tag] = {"size": container.metadata['size_mb'],
                                                                            "id":   container.id }
        # Generate data on the level of collections
        else:
            data[collection.name] = {'size': collection.total_size(),
                                     'id': collection.id,
                                     'n': collection.containers.count() }
                
    return data


def get_filtered_collections(request):
    '''return all collections or only public, given user accessing
    this function will return all collections based on a permission level
    '''
    private = True
    if not request.user.is_anonymous():
        if request.user.is_superuser or request.user.is_staff is True:
             private = True

    if not private:
        return Collection.objects.all()
    return Collection.objects.filter(private=False) 



### Treemap Views and Context


def generate_treemap_context(request):
    collections = get_filtered_collections(request)
    containers = Container.objects.filter(collection__in=collections)
    date = datetime.datetime.now().strftime('%m-%d-%y')
    return {"generation_date": date,
            "containers_count": containers.count(),
            "collections_count": collections.count() }
    

def containers_treemap(request):
    '''show disk usage with a container treemap, 
       for all containers across collections.
    '''
    context = generate_treemap_context(request)   
    if context['containers_count'] >= settings.VISUALIZATION_TREEMAP_COLLECTION_SWITCH:
        return collections_treemap(request,context)
    return render(request, "singularity/containers_treemap.html", context)


def collections_treemap(request,context=None):
    ''' collection treemap shows total size of a collection'''
    if context is None:
        context = generate_treemap_context(request)
    return render(request, "singularity/collections_treemap.html", context)


def collection_treemap(request,cid):
    ''' collection treemap shows size of containers across a single collection'''
    try:
        collection = Collection.objects.get(id=cid)
    except Collection.DoesNotExist:
        messages.info(request,"This collection could not be found.")
        return redirect("collections_treemap")

    if not collection.has_view_permission(request):
        messages.info(request,"You don't have permission to view this collection.")
        return redirect("collections_treemap")

    context = {'collection':collection,
               'generation_date': datetime.datetime.now().strftime('%m-%d-%y')}

    return render(request, "singularity/collection_treemap.html", context)



### Size Data Files Read into D3

def base_size_data(request, collection_level=False, collections=None):
    if collections is None:
        collections = get_filtered_collections(request)
    collections = generate_size_data(collections, collection_level)
    return {'collections':collections}

def container_size_data(request):
    context = base_size_data(request)
    return render(request, 'singularity/container_size_data.csv', context)


def collection_size_data(request):
    ''' generate container size data for all collections
    '''
    context = base_size_data(request, collection_level=True)
    return render(request, 'singularity/collection_size_data.csv', context)


def single_collection_size_data(request,cid):
    ''' generate size data for single collection treemap
    '''
    try:
        collection = Collection.objects.get(id=cid)
    except Collection.DoesNotExist:
        messages.info(request,"This collection could not be found.")
        return redirect("collections_treemap")

    if not collection.has_view_permission(request):
        messages.info(request,"You don't have permission to view this collection.")
        return redirect("collections_treemap")

    context = base_size_data(request, 
                             collection_level=False,
                             collections=[collection])
    return render(request, 'singularity/container_size_data.csv', context)
