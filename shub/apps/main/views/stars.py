'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from shub.apps.main.models import (
    Collection,
    Star
)

from django.http.response import Http404
from shub.settings import (
    VIEW_RATE_LIMIT as rl_rate, 
    VIEW_RATE_LIMIT_BLOCK as rl_block
)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models.aggregates import Count
from django.http import JsonResponse
from ratelimit.decorators import ratelimit
from .collections import get_collection


################################################################################
# COLLECTIONS ##################################################################
################################################################################

def collection_stars(request):
    '''This is a "favorite" view of collections ordered based on number of stars.
    '''
   
    # Favorites based on stars
    collections = Collection.objects.filter(private=False).annotate(Count('star', distinct=True)).order_by('-star__count')
    collections = [x for x in collections if x.star__count > 0]
    context = {"collections": collections}
    return render(request, 'stars/collection_stars.html', context)


def collection_downloads(request):
    '''This is a "favorite" view of collections ordered based on number of downloads.
    '''

    from shub.apps.logs.models import APIRequestCount
    favorites = APIRequestCount.objects.filter(method="get",
                                               path__contains="ContainerDetailByName").order_by('-count')

    context = {"favorites": favorites}
    return render(request, 'stars/collection_downloads.html', context)


################################################################################
# COLLECTION STARS
################################################################################

def star_collection(request, cid):
    '''change favorite status of collection. If it's favorited, unfavorite by deleting
       the star. If not, then create it.
    '''
    if not request.user.is_authenticated:
        raise Http404

    collection = get_collection(cid)
    try:
        star = Star.objects.get(user=request.user,
                                collection=collection)
    except:
        star = None

    if star is None:
        star = Star.objects.create(user=request.user,
                                   collection=collection)
        star.save()
        status = {'status':'added'}
    else:
        star.delete()
        status = {'status':'removed'}

    return JsonResponse(status)
