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

from shub.apps.users.models import User
from shub.apps.main.models import Collection, Star
from shub.apps.logs.models import APIRequestCount 
from django.db.models.aggregates import Count
from django.contrib import messages

from django.db.models import Q, Sum
from django.http import (
    HttpResponseForbidden,
)

from django.shortcuts import (
    render, 
    redirect,
    get_object_or_404
)


from django.contrib.auth.decorators import login_required


@login_required
def view_token(request):
    if request.user.is_superuser or request.user.admin is True:
        return render(request, 'users/token.html')
    else:
        messages.info(request,"You are not allowed to perform this action.")
        return redirect('collections')


def view_profile(request, username=None):
    '''view a user's profile'''

    if not username:
        if not request.user:
            messages.info(request,"You must select a user or be logged in to view a profile.")
            return redirect('collections')
        user = request.user
    else:
        user = get_object_or_404(User, username=username)

    if user == request.user:
        collections = Collection.objects.filter(owner=user).annotate(Count('star', distinct=True)).order_by('-star__count')
    else:
        collections = Collection.objects.filter(owner=user, private=False).annotate(Count('star', distinct=True)).order_by('-star__count')

    # Total Starred Collections
    stars = Star.objects.filter(collection__owner=user).count()
    favorites = Star.objects.filter(user=user)

    # Total Downloads Across Collections
    downloads = APIRequestCount.objects.filter(
                   Q(method='get', path__contains="ContainerDetailByName", collection__owner=user) |
                   Q(method='get', path__contains="ContainerBasicByName", collection__owner=user)).aggregate(Sum('count'))['count__sum']


    context = {'profile': user,
               'collections': collections,
               'downloads': downloads,
               'stars': stars,
               'favorites': favorites}

    return render(request, 'users/profile.html', context)
