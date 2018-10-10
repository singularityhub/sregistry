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


from django.shortcuts import render
from django.template.context import RequestContext
from django.db.models import Q


# Search Pages #################################################################

def search_view(request):
    context = {'active':'share'}
    return render(request, 'search/search.html', context)


def search_query(request,query=None):
    '''query is a post, and results returned immediately'''
    from shub.apps.main.query import collection_query
    context = {'submit_result':'anything'}
    if query is not None:
        results = collection_query(query)
        context["results"] = results
 
    return render(request, 'search/search_single_page.html', context)


def container_search(request):
    '''container_search is the ajax driver to show results for a container search.
    by default we search container collection name.
    ''' 
    from shub.apps.main.query import collection_query
    if request.is_ajax():
        q = request.GET.get('q')
        if q is not None:    
            results = collection_query(q)
            context = {"results":results,
                       "submit_result": "anything"}

            return render(request, 'search/result.html', context)
