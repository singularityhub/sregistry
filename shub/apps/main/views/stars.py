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

from django.db.models.aggregates import Count
from django.http import JsonResponse
from django.http.response import Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

import os
import re
import uuid


###############################################################################################
# COLLECTIONS #################################################################################
###############################################################################################

def starred_collections(request):
    '''return view of collections to user with number of stars.'''
    collections = Collection.objects.filter(
                              private=False).annotate(Count('star', distinct=True)).order_by('-star__count')
    collections = [x for x in collections if x.star__count>0]
    context = {"collections": collections }
    return render(request, 'stars/collections.html', context)
