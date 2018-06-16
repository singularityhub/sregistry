'''

Copyright (C) 2017-2018 The Board of Trustees of the Leland Stanford Junior
University.
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

from shub.logger import bot
from urllib.parse import unquote
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from django.shortcuts import redirect

from shub.apps.main.models import Collection
from sregistry.main.registry.auth import generate_timestamp
from shub.apps.api.utils import ( 
    get_request_user,
    has_permission,
    validate_request
)

from rest_framework.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView

import os

# Terminal Upload


@csrf_exempt
def upload_complete(request):
    '''view called on /api/upload/complete after nginx upload module finishes.
    '''
    from shub.apps.api.actions.create import upload_container

    if request.method == "POST":

        path = request.POST.get('file1.path')
        size = request.POST.get('file1.size')
        cid = request.POST.get('collection')
        filename = request.POST.get('file1.name')
        name = request.POST.get('name')
        version = request.POST.get('file1.md5')
        auth = request.META.get('HTTP_AUTHORIZATION', None)
        tag = request.POST.get('tag')
        csrftoken = request.META.get('CSRF_COOKIE')

        if auth is None and csrftoken is None:

            # Clean up the file
            if os.path.exists(filename):
                os.remove(path)

            raise PermissionDenied(detail="Authentication Required")

        # at this point, the collection MUST exist
        try:
            collection = Collection.objects.get(id=cid)
        except Collection.DoesNotExist:
            raise PermissionDenied(detail="Authentication Required")
    
        # If not defined, coming from terminal
        web_interface = True
        if csrftoken is None:
            web_interface = False
            owner = get_request_user(auth)
            timestamp = generate_timestamp()
            payload = "upload|%s|%s|%s|%s|" %(collection.name,
                                              timestamp,
                                              name,
                                              tag)

            # Validate Payload
            if not validate_request(auth, payload, "upload", timestamp):
                raise PermissionDenied(detail="Unauthorized")

            if not has_permission(auth, collection, pull_permission=False):
                raise PermissionDenied(detail="Unauthorized")

        else:
            owner = request.user

        # If tag is provided, add to name
        if tag is not None:
            name = "%s:%s" %(name, tag)
        
        # Expected params are upload_id, name, md5, and cid
        upload_container(cid = collection.id,
                         user = owner,
                         version = version,
                         upload_id = path,
                         name = name,
                         size = size)

        if web_interface is True:
            return redirect(collection.get_absolute_url())
        return JsonResponse({"message":"Upload Complete"})

    return redirect('collections')


class UploadUI(LoginRequiredMixin, TemplateView):
    template_name = 'routes/upload.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['collection'] = Collection.objects.get(id=context['cid'])
        return context
