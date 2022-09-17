"""

Copyright (C) 2017-2022 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

import datetime

from django.db.models import Q
from django.shortcuts import render
from ratelimit.decorators import ratelimit

from shub.apps.main.models import Collection, Container
from shub.settings import VIEW_RATE_LIMIT as rl_rate
from shub.settings import VIEW_RATE_LIMIT_BLOCK as rl_block

################################################################################
# FILE SYSTEM USAGE ############################################################
################################################################################


def generate_size_data(collections):
    """generate a datastructure that can be rendered as:
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
    """
    data = dict()
    for collection in collections:

        collection_name = collection.name
        if "/" in collection_name:
            collection_name = collection_name.split("/")[0]

        if collection_name not in data:
            data[collection_name] = {}

        # Generate data on the level of collections by default
        # Size used to be container sizes, but now we return just counts
        data[collection_name] = {
            "size": collection.containers.count(),
            "id": collection.id,
            "n": collection.containers.count(),
        }

    return data


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def get_filtered_collections(request):
    """return all collections or only public, given user accessing
    this function will return all collections based on a permission level
    """
    if request.user.is_superuser or request.user.is_staff:
        collections = Collection.objects.all()
    else:
        collections = Collection.objects.filter(
            Q(owners=request.user) | Q(contributors=request.user) | Q(private=False)
        )
    return collections


### Treemap Views and Context


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def generate_treemap_context(request):
    collections = get_filtered_collections(request)
    containers = Container.objects.filter(collection__in=collections)
    date = datetime.datetime.now().strftime("%m-%d-%y")
    return {
        "generation_date": date,
        "containers_count": containers.count(),
        "collections_count": collections.count(),
    }


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def collections_treemap(request, context=None):
    """collection treemap shows total size of a collection"""
    if context is None:
        context = generate_treemap_context(request)
    return render(request, "singularity/collections_treemap.html", context)


### Size Data Files Read into D3


def base_size_data(request, collections=None):
    if collections is None:
        collections = get_filtered_collections(request)
    collections = generate_size_data(collections)
    return {"collections": collections}


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def container_size_data(request):
    context = base_size_data(request)
    return render(request, "singularity/container_size_data.csv", context)


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def collection_size_data(request):
    """generate container size data for all collections"""
    context = base_size_data(request)
    return render(request, "singularity/collection_size_data.csv", context)
