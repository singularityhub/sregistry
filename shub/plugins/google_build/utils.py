"""

Copyright (C) 2016-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from datetime import datetime, timedelta
from django.http import JsonResponse
from django.conf import settings
from oauth2client.client import GoogleCredentials
from googleapiclient import discovery
import google.auth.transport.requests
import google.auth
import google.auth.iam
from sregistry.logger import RobotNamer
import hashlib
import hmac
import json
import jwt
import binascii
import collections
import re
import requests
from urllib.parse import unquote
from six.moves.urllib.parse import quote
import uuid


################################################################################
# REQUESTS
################################################################################


def POST(url, headers, data=None, params=None):
    """post_url will use the requests library to post to a url"""
    if data is not None:
        return requests.post(url, headers=headers, data=json.dumps(data))
    return requests.get(url, headers=headers)


def DELETE(url, headers, data=None, params=None):
    """issue a delete reqest, with or without data and params."""
    if data is not None:
        return requests.delete(url, headers=headers, data=json.dumps(data))
    return requests.delete(url, headers=headers)


def format_params(url, params):
    """format_params will add a list of params (?key=value) to a url

    Parameters
    ==========
    params: a dictionary of params to add
    url: the url to add params to
    """
    # Always try to get 100 per page
    params["per_page"] = 100
    count = 0
    for param, value in params.items():
        if count == 0:
            url = "%s?%s=%s" % (url, param, value)
        else:
            url = "%s&%s=%s" % (url, param, value)
        count += 1
    return url


def paginate(url, headers, min_count=30, start_page=1, params=None, limit=None):
    """paginate will send posts to a url with post_url
    until the results count is not exceeded

    Parameters
    ==========
    min_count: the results count to go to
    start_page: the starting page
    """
    if params is None:
        params = dict()
    result = []
    result_count = 1000
    page = start_page
    while result_count >= 30:

        # If the user set a limit, honor it
        if limit is not None:
            if len(result) >= limit:
                return result

        params["page"] = page
        paginated_url = format_params(url, params)
        new_result = requests.get(paginated_url, headers=headers).json()
        result_count = len(new_result)

        # If the user triggers bad credentials, empty repository, stop
        if isinstance(new_result, dict):
            return result

        result = result + new_result
        page += 1
    return result


def validate_payload(collection, payload, request_signature):
    """validate_payload will retrieve a collection secret, use it
    to create a hexdigest of the payload (request.body) and ensure
    that it matches the signature in the header). This is what we use
    for GitHub webhooks. The secret used is NOT the collection secret,
    but a different one for GitHub.

    Parameters
    ==========
    collection: the collection object with the secret
    payload: the request body sent by the service
    request_signature: the signature to compare against
    """
    secret = collection.metadata["github"]["secret"].encode(
        "utf-8"
    )  # converts to bytes
    digest = hmac.new(secret, digestmod=hashlib.sha1, msg=payload).hexdigest()
    signature = "sha1=%s" % (digest)
    return hmac.compare_digest(signature, request_signature)


################################################################################
# JWT
################################################################################


def get_container_payload(container):
    """a helper function to return a consistent container payload.

    Parameters
    ==========
    container: a container object to get a payload for
    """
    return {
        "collection": container.collection.id,
        "container": container.id,
        "robot-name": container.metadata["builder"]["robot_name"],
        "tag": container.tag,
    }


def create_container_payload(container):
    """a helper function to create a consistent container payload.

    Parameters
    ==========
    container: a container object to create a payload for
    """
    if "builder" not in container.metadata:
        container.metadata["builder"] = {}

    if "robot_name" not in container.metadata["builder"]:
        container.metadata["builder"]["robot_name"] = RobotNamer().generate()

    # Always create a new secret
    container.metadata["builder"]["secret"] = str(uuid.uuid4())
    container.save()
    return get_container_payload(container)


def clear_container_payload(container):
    """after we receive the build response, we clear the payload metadata
    so it cannot be used again. This function does not save, but returns
    the container for the calling function to do so.

    Parameters
    ==========
    container: a container object to clear payload secrets for
    """
    if "builder" in container.metadata:
        if "robot_namer" in container.metadata["builder"]:
            del container.metadata["builder"]["robot_namer"]

        if "secret" in container.metadata["builder"]:
            del container.metadata["builder"]["secret"]

    return container


def validate_jwt(container, params):
    """Given a container (with a build secret and other metadata) validate
    a token (if it exists). If valid, return true. Otherwise,
    return False.
    """
    if "token" not in params:
        return False

    # The secret is removed after one response
    if "secret" not in container.metadata["builder"]:
        return False

    secret = container.metadata["builder"]["secret"]

    # Validate the payload
    try:
        payload = jwt.decode(params["token"], secret, algorithms=["HS256"])
    except (jwt.DecodeError, jwt.ExpiredSignatureError):
        return False

    # Compare against what we know
    valid_payload = get_container_payload(container)

    # Every field must be equal
    for key, _ in valid_payload.items():
        if key not in payload:
            return False
        if payload[key] != valid_payload[key]:
            return False

    return True


def generate_jwt_token(secret, payload, algorithm="HS256"):
    """given a secret, an expiration in seconds, and an algorithm, generate
    a jwt token to add as a header to the build response.

    Parameters
    ==========
    secret: the container builder secret, only used once
    payload: the payload to encode
    algorithm: the algorithm to use.
    """
    # Add an expiration of 8 hours to the payload
    expires_in = settings.SREGISTRY_GOOGLE_BUILD_EXPIRE_SECONDS
    payload["exp"] = datetime.utcnow() + timedelta(seconds=expires_in)
    return jwt.encode(payload, secret, algorithm).decode("utf-8")


def generate_signed_url(storage_path, expiration=None, headers=None, http_method="GET"):
    """generate_signed_url will generate a signed url for a storage object,
    given that it's allowance is less than the GET limit. The signed URL
    ONLY needs to endure for the post request, so we limit it to 10 seconds.
    https://cloud.google.com/storage/docs/access-control/signing-urls-manually.

    # This function needs to be tested
    """
    # Can't get a signed URL for a container without image
    if storage_path is None:
        return storage_path

    # The expiration time in seconds, cannot exceed 604800 (7 days)
    if expiration is None:
        expiration = settings.CONTAINER_SIGNED_URL_EXPIRE_SECONDS  # 10

    credentials, _ = google.auth.default()
    storage_credentials = GoogleCredentials.get_application_default()
    service = discovery.build("storage", "v1", credentials=storage_credentials)

    bucket_name = get_bucket_name(storage_path)
    bucket = service.buckets().get(bucket=bucket_name).execute()

    object_name = get_object_name(storage_path, bucket_name)
    if object_name is None:
        return object_name

    # The blob must exist
    try:
        service.objects().get(bucket=bucket["id"], object=object_name).execute()
    except:  # HttpError:
        return None

    escaped_object_name = quote(object_name, safe="")
    canonical_uri = "/{}/{}".format(bucket_name, escaped_object_name)

    # Generate the timestamp
    datetime_now = datetime.utcnow()
    request_timestamp = datetime_now.strftime("%Y%m%dT%H%M%SZ")
    datestamp = datetime_now.strftime("%Y%m%d")

    # Prepare the signer (will use correct client email)
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)

    # Prepare credential for service account
    client_email = credentials.service_account_email
    credential_scope = "{}/auto/storage/goog4_request".format(datestamp)
    credential = "{}/{}".format(client_email, credential_scope)

    if headers is None:
        headers = dict()
    headers["host"] = "storage.googleapis.com"

    canonical_headers = ""
    ordered_headers = collections.OrderedDict(sorted(headers.items()))
    for k, v in ordered_headers.items():
        lower_k = str(k).lower()
        strip_v = str(v).lower()
        canonical_headers += "{}:{}\n".format(lower_k, strip_v)

    signed_headers = ""
    for k, _ in ordered_headers.items():
        lower_k = str(k).lower()
        signed_headers += "{};".format(lower_k)
    signed_headers = signed_headers[:-1]  # remove trailing ';'

    query_parameters = dict()
    query_parameters["X-Goog-Algorithm"] = "GOOG4-RSA-SHA256"
    query_parameters["X-Goog-Credential"] = credential
    query_parameters["X-Goog-Date"] = request_timestamp
    query_parameters["X-Goog-Expires"] = expiration
    query_parameters["X-Goog-SignedHeaders"] = signed_headers

    canonical_query_string = ""
    ordered_query_parameters = collections.OrderedDict(sorted(query_parameters.items()))
    for k, v in ordered_query_parameters.items():
        encoded_k = quote(str(k), safe="")
        encoded_v = quote(str(v), safe="")
        canonical_query_string += "{}={}&".format(encoded_k, encoded_v)
    canonical_query_string = canonical_query_string[:-1]  # remove trailing ';'

    canonical_request = "\n".join(
        [
            http_method,
            canonical_uri,
            canonical_query_string,
            canonical_headers,
            signed_headers,
            "UNSIGNED-PAYLOAD",
        ]
    )

    canonical_request_hash = hashlib.sha256(canonical_request.encode()).hexdigest()

    string_to_sign = "\n".join(
        [
            "GOOG4-RSA-SHA256",
            request_timestamp,
            credential_scope,
            canonical_request_hash,
        ]
    )
    signer = google.auth.iam.Signer(request, credentials, client_email)

    signature = binascii.hexlify(signer.sign(string_to_sign)).decode()

    host_name = "https://storage.googleapis.com"
    signed_url = "{}{}?{}&X-Goog-Signature={}".format(
        host_name, canonical_uri, canonical_query_string, signature
    )
    return signed_url


def get_object_name(storage_path, bucket_name):
    """based on a storage bucket and path, return an object path
    that can be used for a signed url.
    """
    regexp = (
        "https://www.googleapis.com/download/storage/v[0-9]{1}/b/%s/o/(?P<path>.+)[?]"
        % bucket_name
    )
    match = re.search(regexp, storage_path)
    if match is None:
        return match

    # singularityhub/github.com/<user>/<repo>/<commit>/<hash>
    return unquote(match.groupdict()["path"])


def get_bucket_name(object_name):
    """get_bucket_name will return the default bucket name. We first try
    to get from the client settings, otherwise we get from the object.
    """
    # First default to what is defined with server
    if hasattr(settings, "SREGISTRY_GOOGLE_STORAGE_BUCKET"):
        return settings.SREGISTRY_GOOGLE_STORAGE_BUCKET

    # https://www.googleapis.com/download/storage/v1/b/<bucket>/o
    parts = re.split("/v[0-9]{1}/b/", object_name)
    bucket_name = parts[1].split("/")[0]
    print("Bucket name is %s" % bucket_name)
    return bucket_name


################################################################################
# HEADERS/NAMING
################################################################################


def check_headers(request, headers):
    """check_headers will ensure that header keys are included in
    a request. If one is missing, returns False

    Parameters
    ==========
    request: the request object
    headers: the headers (keys) to check for
    """
    for header in headers:
        if header not in request.META:
            return False
    return True


def get_default_headers():
    """get_default_headers will return content-type json, etc."""
    headers = {"Content-Type": "application/json"}
    return headers


def JsonResponseMessage(status=500, message=None, status_message="error"):
    response = {"status": status_message}
    if message is not None:
        response["message"] = message
    return JsonResponse(response, status=status)


################################################################################
# FORMATTING
################################################################################


def convert_size(size_bytes, to, bsize=1024):
    """A function to convert bytes to a human friendly string."""
    a = {"KB": 1, "MB": 2, "GB": 3, "TB": 4, "PB": 5, "EB": 6}
    r = float(size_bytes)
    for _ in range(a[to]):
        r = r / bsize
    return r


def load_body(request):
    """load the body of a request."""
    if isinstance(request.body, bytes):
        payload = json.loads(request.body.decode("utf-8"))
    else:
        payload = json.loads(request.body)
    return payload
