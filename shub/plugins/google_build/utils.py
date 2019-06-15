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

from datetime import datetime, timedelta
import hashlib
import hmac
import json
import jwt
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
       that it matches the signature in the header). This is what we use
       for GitHub webhooks. The secret used is NOT the collection secret,
       but a different one for GitHub.

       Parameters
       ==========
       collection: the collection object with the secret
       payload: the request body sent by the service
       request_signature: the signature to compare against
    '''
    secret = collection.metadata['github']['secret'].encode('utf-8') # converts to bytes
    digest = hmac.new(secret,digestmod=hashlib.sha1,
                      msg=payload).hexdigest()
    signature = 'sha1=%s' %(digest)
    return hmac.compare_digest(signature, request_signature)


################################################################################
# JWT
################################################################################

def get_container_payload(container):
    '''a helper function to return a consistent container payload.

       Parameters
       ==========
       container: a container object to get a payload for
    '''
    return {
        "collection": container.collection.id,
        "container": container.id,
        "robot-name": container.metadata['builder']['robot_name'],
        "tag": container.tag
    }


def create_container_payload(container):
    '''a helper function to create a consistent container payload.

       Parameters
       ==========
       container: a container object to create a payload for
    '''
    if "builder" not in container.metadata:
        container.metadata['builder'] = {}

    if "robot_name" not in container.metadata["builder"]:
        container.metadata['builder']['robot_name'] = RobotNamer().generate()

    # Always create a new secret
    container.metadata['builder']['secret'] = str(uuid.uuid4())
    container.save()
    return get_container_payload(container)


def clear_container_payload(container):
    '''after we receive the build response, we clear the payload metadata
       so it cannot be used again. This function does not save, but returns
       the container for the calling function to do so.

       Parameters
       ==========
       container: a container object to clear payload secrets for
    '''
    if "builder" in container.metadata:
        if "robot_namer" in container.metadata['builder']:
            del container.metadata['builder']['robot_namer']

        if "secret" in container.metadata['builder']:
            del container.metadata['builder']['secret']

    return container


def validate_jwt(container, headers)
    '''Given a container (with a build secret and other metadata) validate
       a token header (if it exists). If valid, return true. Otherwise, 
       return False.
    '''
    if "token" not in request.headers:
        print('TOKEN NOT IN HEADERS')
        return False

    # The secret is removed after one response
    if "secret" not in container.metadata['builder']:
        print('SECRET NOT IN HEADERS')
        return False
   
    secret = container.metadata['builder']['secret']

    # Validate the payload
    try:
        payload = jwt.decode(request.headers['token'], secret, algorithms=["HS256"])
    except (jwt.DecodeError, jwt.ExpiredSignatureError):
        print('TOKEN INVALID')
        return False

    # Compare against what we know
    valid_payload = get_container_payload(container)

    # Must be equally sized dicts
    if len(valid_payload) != len(payload):
        print('INVALID LENGTH')
        return False

    # Every field must be equal
    for key, val in valid_payload.items():
        if key not in payload:
            print('%s not in payload' % key)
            return False
        if payload[key] != valid_payload[key]:
            print('%s invalid' % key)
            return False

    return True        


def generate_jwt_token(secret, payload, algorithm="HS256"):
    '''given a secret, an expiration in seconds, and an algorithm, generate
       a jwt token to add as a header to the build response.

       Parameters
       ==========
       secret: the container builder secret, only used once
       payload: the payload to encode
       algorithm: the algorithm to use.
    '''
    # Add an expiration of 8 hours to the payload
    expires_in = settings.SREGISTRY_GOOGLE_BUILD_EXPIRE_SECONDS
    payload['exp'] = datetime.utcnow() + timedelta(seconds=expires_in)
    return jwt.encode(payload, secret, algorithm).decode('utf-8')


################################################################################
# HEADERS/NAMING
################################################################################


def check_headers(request, headers):
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


def convert_size(bytes, to, bsize=1024):
   '''A function to convert bytes to a human friendly string.
   '''
   a = {'KB' : 1, 'MB': 2, 'GB' : 3, 'TB' : 4, 'PB' : 5, 'EB' : 6 }
   r = float(bytes)
   for i in range(a[to]):
       r = r / bsize
   return(r)


def load_body(request):
    '''load the body of a request.
    '''
    if isinstance(request.body, bytes):
        payload = json.loads(request.body.decode('utf-8'))
    else:
        payload = json.loads(request.body)
    return payload
