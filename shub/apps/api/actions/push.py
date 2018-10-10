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

from shub.logger import bot
from django.http import JsonResponse
from rest_framework.exceptions import PermissionDenied

from shub.apps.main.models import Collection
from django.views.decorators.csrf import csrf_exempt
from shub.apps.main.utils import format_collection_name
from shub.apps.api.utils import ( 
    validate_request,
    has_permission, 
    get_request_user
)

import json
import uuid
from sregistry.main.registry.auth import generate_timestamp

@csrf_exempt
def collection_auth_check(request):
    ''' check permissions and 
        return a collection id (cid) if a collection exists and the user
        has permission to upload. If not, a permission denied is returned.
    '''
    auth=request.META.get('HTTP_AUTHORIZATION', None)
  
    # Load the body, which is json with variables
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    # Get variables
    tag=body.get('tag','latest')                                   
    name=body.get('name')
    collection_name = format_collection_name(body.get('collection'))

    print(tag, name, collection_name, auth, body)
    
    # Authentication always required for push
    if auth is None:
        raise PermissionDenied(detail="Authentication Required")

    owner = get_request_user(auth)
    timestamp = generate_timestamp()
    payload = "push|%s|%s|%s|%s|" %(collection_name,
                                    timestamp,
                                    name,
                                    tag)

    # Validate Payload
    print(payload)
    if not validate_request(auth, payload, "push", timestamp):
        raise PermissionDenied(detail="Unauthorized")

    try:
        collection = Collection.objects.get(name=collection_name)

    except Collection.DoesNotExist:
        collection = None

    # Validate User Permissions, either for creating collection or adding
    # Here we have permission if:
    # 1- user collections are enabled with USER_COLLECTIONS
    # 2- the user is a superuser or staff
    # 3- the user is owner of a collection
    if not has_permission(auth, collection, pull_permission=False):
         raise PermissionDenied(detail="Unauthorized")
        
    # If we get here user has create permission, does collection exist?
    if collection is None:
        collection = Collection.objects.create(name=collection_name,
                                               secret=str(uuid.uuid4()))
        collection.save()
        collection.owners.add(owner)
        collection.save()

    # Return json response with collection id
    return JsonResponse({'cid': collection.id })
