'''

Copyright (C) 2016-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from django.http import JsonResponse

from rest_framework.permissions import (
    DjangoObjectPermissions,
    SAFE_METHODS, 
    Http404
)

import hashlib
import hmac
import json
import requests
import re

################################################################################
# REQUESTS
################################################################################


def POST(url,headers, data=None, params=None):
    '''post_url will use the requests library to post to a url
    '''
    if data is not None:
        return requests.post(url,
                             headers=headers,
                             data=json.dumps(data))
    return requests.get(url, headers=headers)


def DELETE(url, headers, data=None, params=None):
    '''issue a delete reqest, with or without data and params.
    '''
    if data is not None:
        return requests.delete(url,
                               headers=headers,
                               data=json.dumps(data))
    return requests.delete(url,headers=headers)


def format_params(url, params):
    '''format_params will add a list of params (?key=value) to a url

       Parameters
       ==========
       params: a dictionary of params to add
       url: the url to add params to
    '''
    # Always try to get 100 per page
    params["per_page"] = 100
    count=0
    for param,value in params.items():
        if count == 0:
            url = "%s?%s=%s" %(url,param,value)
        else:
            url = "%s&%s=%s" %(url,param,value)
        count+=1
    return url


def paginate(url,headers,min_count=30,start_page=1,params=None, limit=None):
    '''paginate will send posts to a url with post_url
       until the results count is not exceeded

       Parameters
       ========== 
       min_count: the results count to go to
       start_page: the starting page
    '''
    if params == None:
        params = dict()
    result = []
    result_count = 1000
    page = start_page
    while result_count >= 30:

        # If the user set a limit, honor it
        if limit is not None:
            if len(result) >= limit:
                return result

        params['page'] = page
        paginated_url = format_params(url,params)
        new_result = requests.get(paginated_url, headers=headers).json()
        result_count = len(new_result)

        # If the user triggers bad credentials, empty repository, stop
        if isinstance(new_result,dict):
            return result
        
        result = result + new_result
        page += 1
    return result


def validate_payload(collection, payload, request_signature):
    '''validate_payload will retrieve a collection secret, use it
       to create a hexdigest of the payload (request.body) and ensure
       that it matches the signature in the header)

       Parameters
       ==========
       collection: the collection object with the secret
       payload: the request body sent by the service
       request_signature: the signature to compare against
    '''
    secret = collection.secret.encode('utf-8') # converts to bytes
    digest = hmac.new(secret,digestmod=hashlib.sha1,
                      msg=payload).hexdigest()
    signature = 'sha1=%s' %(digest)
    return hmac.compare_digest(signature, request_signature)


################################################################################
# HEADERS/NAMING
################################################################################


def check_headers(request,headers):
    '''check_headers will ensure that header keys are included in
       a request. If one is missing, returns False
 
       Parameters
       ==========
       request: the request object
       headers: the headers (keys) to check for
    '''
    for header in headers:
        if header not in request.META:
            return False
    return True


def get_default_headers():
    '''get_default_headers will return content-type json, etc.
    '''
    headers = {"Content-Type": "application/json"}
    return headers


def JsonResponseMessage(status=500, message=None, status_message='error'):
    response = {'status': status_message}
    if message is not None:
        response['message'] = message
    return JsonResponse(response, status=status)


################################################################################
# FORMATTING
################################################################################

def load_body(request):
    '''load the body of a request.
    '''
    if isinstance(request.body, bytes):
        payload = json.loads(request.body.decode('utf-8'))
    else:
        payload = json.loads(request.body)
    return payload
