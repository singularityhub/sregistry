"""

Copyright (C) 2020-2022 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

import hashlib
import hmac
from datetime import datetime

from boto3 import Session
from botocore.client import Config
from minio import Minio
from minio.compat import queryencode, urlsplit
from minio.error import InvalidArgumentError
from minio.signer import (
    collections,
    generate_canonical_request,
    generate_credential_string,
    generate_signing_key,
    generate_string_to_sign,
    get_signed_headers,
)

from shub.apps.main.models import Container
from shub.settings import (
    DISABLE_MINIO_CLEANUP,
    MINIO_BUCKET,
    MINIO_EXTERNAL_SERVER,
    MINIO_REGION,
    MINIO_ROOT_PASSWORD,
    MINIO_ROOT_USER,
    MINIO_SERVER,
    MINIO_SSL,
)

# Signature version '4' algorithm.
_SIGN_V4_ALGORITHM = "AWS4-HMAC-SHA256"

MINIO_HTTP_PREFIX = "https://" if MINIO_SSL else "http://"

minioClient = Minio(
    MINIO_SERVER,
    region=MINIO_REGION,
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=MINIO_SSL,
)

minioExternalClient = Minio(
    MINIO_EXTERNAL_SERVER,
    region=MINIO_REGION,
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=MINIO_SSL,
)

if not minioClient.bucket_exists(MINIO_BUCKET):
    minioClient.make_bucket(MINIO_BUCKET)

session = Session(
    aws_access_key_id=MINIO_ROOT_USER,
    aws_secret_access_key=MINIO_ROOT_PASSWORD,
    region_name=MINIO_REGION,
)


# https://github.com/boto/boto3/blob/develop/boto3/session.py#L185
s3 = session.client(
    "s3",
    verify=MINIO_SSL,
    use_ssl=MINIO_SSL,
    endpoint_url=MINIO_HTTP_PREFIX + MINIO_SERVER,
    region_name=MINIO_REGION,
    config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
)

# signature_versions
# https://github.com/boto/botocore/blob/master/botocore/auth.py#L846
s3_external = session.client(
    "s3",
    verify=MINIO_SSL,
    use_ssl=MINIO_SSL,
    endpoint_url=MINIO_HTTP_PREFIX + MINIO_EXTERNAL_SERVER,
    region_name=MINIO_REGION,
    config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
)


def sregistry_presign_v4(
    method,
    url,
    credentials,
    content_hash_hex,
    region=None,
    headers=None,
    expires=None,
    response_headers=None,
):
    """
    Calculates signature version '4' for regular presigned URLs.
    :param method: Method to be presigned examples 'PUT', 'GET'.
    :param url: URL to be presigned.
    :param credentials: Credentials object with your AWS s3 account info.
    :param region: region of the bucket, it is optional.
    :param headers: any additional HTTP request headers to
       be presigned, it is optional.
    :param expires: final expiration of the generated URL. Maximum is 7days.
    :param response_headers: Specify additional query string parameters.
    :param content_hash_hex: sha256sum of the object.
    """

    # Validate input arguments.
    if not credentials.get().access_key or not credentials.get().secret_key:
        raise InvalidArgumentError("Invalid access_key and secret_key.")

    if region is None:
        region = MINIO_REGION

    if headers is None:
        headers = {}

    # 7 days
    if expires is None:
        expires = "604800"

    request_date = datetime.utcnow()

    parsed_url = urlsplit(url)
    host = remove_default_port(parsed_url)
    headers["Host"] = host
    iso8601Date = request_date.strftime("%Y%m%dT%H%M%SZ")

    headers_to_sign = headers
    # Construct queries.
    query = {}
    query["X-Amz-Algorithm"] = _SIGN_V4_ALGORITHM
    query["X-Amz-Credential"] = generate_credential_string(
        credentials.get().access_key, request_date, region
    )
    query["X-Amz-Date"] = iso8601Date
    query["X-Amz-Expires"] = str(expires)
    if credentials.get().session_token is not None:
        query["X-Amz-Security-Token"] = credentials.get().session_token

    signed_headers = get_signed_headers(headers_to_sign)
    query["X-Amz-SignedHeaders"] = ";".join(signed_headers)

    if response_headers is not None:
        query.update(response_headers)

    # URL components.
    url_components = [parsed_url.geturl()]
    if query is not None:
        ordered_query = collections.OrderedDict(sorted(query.items()))
        query_components = []
        for component_key in ordered_query:
            single_component = [component_key]
            if ordered_query[component_key] is not None:
                single_component.append("=")
                single_component.append(queryencode(ordered_query[component_key]))
            else:
                single_component.append("=")
            query_components.append("".join(single_component))

        query_string = "&".join(query_components)
        if query_string:
            url_components.append("?")
            url_components.append(query_string)
    new_url = "".join(url_components)
    # new url constructor block ends.
    new_parsed_url = urlsplit(new_url)

    canonical_request = generate_canonical_request(
        method, new_parsed_url, headers_to_sign, signed_headers, content_hash_hex
    )
    string_to_sign = generate_string_to_sign(request_date, region, canonical_request)
    signing_key = generate_signing_key(
        request_date, region, credentials.get().secret_key
    )
    signature = hmac.new(
        signing_key, string_to_sign.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    new_parsed_url = urlsplit(new_url + "&X-Amz-Signature=" + signature)
    return new_parsed_url.geturl()


def remove_default_port(parsed_url):
    default_ports = {"http": 80, "https": 443}
    if any(
        parsed_url.scheme == scheme and parsed_url.port == port
        for scheme, port in default_ports.items()
    ):
        # omit default port (i.e. 80 or 443)
        host = parsed_url.hostname
    else:
        host = parsed_url.netloc
    return host


def delete_minio_container(container):
    """A helper function to delete a container in Minio based on not finding
    more than one count for it (indicating that it is not in use by other
    container collections).

    Parameters
    ==========
    container: the container object to get Minio storage from.
    """
    # Ensure that we don't have the container referenced by another collection
    # The verison would be the same, regardless of the collection/container name
    count = Container.objects.filter(version=container.version).count()
    storage = container.get_storage()

    # only delete from Minio not same filename, and if there is only one count
    if count == 1 and not DISABLE_MINIO_CLEANUP:
        print("Deleting no longer referenced container %s from Minio" % storage)
        minioClient.remove_object(MINIO_BUCKET, storage)
        return True
    return False
