"""

Copyright (C) 2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from boto3 import Session
import boto3
from botocore.client import Config

from shub.settings import (
    MINIO_SERVER,
    MINIO_EXTERNAL_SERVER,
    MINIO_BUCKET,
    MINIO_REGION,
    MINIO_SSL,
)
from minio import Minio

import os

MINIO_HTTP_PREFIX = "https://" if MINIO_SSL else "http://"

minioClient = Minio(
    MINIO_SERVER,
    region=MINIO_REGION,
    access_key=os.environ.get("MINIO_ACCESS_KEY"),
    secret_key=os.environ.get("MINIO_SECRET_KEY"),
    secure=MINIO_SSL,
)

minioExternalClient = Minio(
    MINIO_EXTERNAL_SERVER,
    region=MINIO_REGION,
    access_key=os.environ.get("MINIO_ACCESS_KEY"),
    secret_key=os.environ.get("MINIO_SECRET_KEY"),
    secure=MINIO_SSL,
)

if not minioClient.bucket_exists(MINIO_BUCKET):
    minioClient.make_bucket(MINIO_BUCKET)

session = Session(
    aws_access_key_id=os.environ.get("MINIO_ACCESS_KEY"),
    aws_secret_access_key=os.environ.get("MINIO_SECRET_KEY"),
    region_name=MINIO_REGION,
)


# https://github.com/boto/boto3/blob/develop/boto3/session.py#L185
s3 = session.client(
    "s3",
    verify=False,
    use_ssl=MINIO_SSL,
    endpoint_url=MINIO_HTTP_PREFIX + MINIO_SERVER,
    region_name=MINIO_REGION,
    config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
)

# signature_versions
# https://github.com/boto/botocore/blob/master/botocore/auth.py#L846
s3_external = session.client(
    "s3",
    use_ssl=MINIO_SSL,
    region_name=MINIO_REGION,
    endpoint_url=MINIO_HTTP_PREFIX + MINIO_EXTERNAL_SERVER,
    verify=False,
    config=Config(signature_version="s2", s3={"addressing_style": "path"}),
)

# THINGS TO TRY
# change algorithm to not include host header (but then
# try to set host header to something else
