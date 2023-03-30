"""

Copyright 2017-2023 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.shortcuts import render
from ratelimit.decorators import ratelimit

from shub.settings import VIEW_RATE_LIMIT as rl_rate
from shub.settings import VIEW_RATE_LIMIT_BLOCK as rl_block

# Search Pages #################################################################


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def search_view(request):
    context = {"active": "share"}
    return render(request, "search/search.html", context)


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def search_query(request, query=None):
    """query is a post, and results returned immediately"""
    from shub.apps.main.query import collection_query

    context = {"submit_result": "anything"}
    if query is not None:
        results = collection_query(query)
        context["results"] = results

    return render(request, "search/search_single_page.html", context)


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def container_search(request):
    """container_search is the ajax driver to show results for a container search.
    by default we search container collection name.
    """
    from shub.apps.main.query import collection_query

    if request.is_ajax():
        q = request.GET.get("q")
        if q is not None:
            results = collection_query(q)
            context = {"results": results, "submit_result": "anything"}

            return render(request, "search/result.html", context)
