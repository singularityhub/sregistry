'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from shub.apps.users.models import User
from shub.apps.main.models import Collection, Star
from shub.apps.logs.models import APIRequestCount
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models.aggregates import Count
from django.shortcuts import render, redirect
from shub.settings import USER_COLLECTIONS
from django.db.models import Q, Sum


@login_required
def view_token(request):
    ''' tokens are valid for pushing (creating collections) and only available
        to superusers or staff, unless USER_COLLECTIONS is set to True. If
        user's are allowed to create collections, they can push to those for
        which they are an owner or contributor. 
    '''
    return render(request, 'users/token.html')



def view_profile(request, username=None):
    '''view a user's profile, including collections and download counts
    '''

    message = "You must select a user or be logged in to view a profile."
    if not username:
        if not request.user:
            messages.info(request, message)
            return redirect('collections')
        user = request.user
    else:
        user = get_object_or_404(User, username=username)

    if user == request.user:
        collections = Collection.objects.filter(owners=user).annotate(
                      Count('star', distinct=True)).order_by('-star__count')
    else:
        collections = Collection.objects.filter(owners=user, 
                          private=False).annotate(Count('star', 
                          distinct=True)).order_by('-star__count')

    # Total Starred Collections

    stars = Star.objects.filter(collection__owners=user).count()
    favorites = Star.objects.filter(user=user)

    # Total Downloads Across Collections

    downloads = APIRequestCount.objects.filter(
                   Q(method='get', 
                     path__contains="ContainerDetailByName", 
                     collection__owners=user) |
                   Q(method='get', 
                     path__contains="ContainerBasicByName", 
                     collection__owners=user)).aggregate(Sum('count'))

    downloads = downloads['count__sum']

    context = {'profile': user,
               'collections': collections,
               'downloads': downloads,
               'stars': stars,
               'favorites': favorites}

    return render(request, 'users/profile.html', context)
