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
    Collection
)

from django.template import loader, Context
from django.http import HttpResponse
from shub.settings import BASE_DIR

from django.shortcuts import (
    render, 
    redirect
)

from django.contrib import messages

import datetime
import os
import json
import re
import shutil


###############################################################################################
# FILE SYSTEM USAGE ###########################################################################
###############################################################################################

def generate_size_data(collections):
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
        containers = collection.containers.all()
        for container in containers:
            if container.name not in data[collection.name]:
                data[collection.name][container.name] = dict()
            if 'size_mb' in container.metadata:
                data[collection.name][container.name][container.tag] = {"size": container.metadata['size_mb'],
                                                                        "id":   container.id }
    return data



def get_filtered_collections(request):
    '''return all collections or only public, given user accessing'''
    private = True
    if not request.user.is_anonymous():
        if request.user.is_superuser or request.user.admin is True:
             private = True

    if not private:
        return Collection.objects.filter()
    return Collection.objects.filter(private=False) 


def container_treemap(request):
    '''show disk usage with a container treemap.
    '''
    collections = get_filtered_collections(request)
    containers = Container.objects.filter(collection__in=collections)
    date = datetime.datetime.now().strftime('%m-%d-%y')
    context = {"generation_date": date,
               "containers_count": containers.count(),
               "collections_count": collections.count() }
    return render(request, 'singularity/container_treemap.html', context)



def container_size_data(request):
    collections = get_filtered_collections(request)
    collections = generate_size_data(collections)
    context = {'collections':collections}

    return render(request, 'singularity/container_size_data.csv', context)
