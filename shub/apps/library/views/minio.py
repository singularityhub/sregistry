"""

Copyright (C) 2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from shub.settings import (
    MINIO_SERVER,
    MINIO_EXTERNAL_SERVER,
    MINIO_BUCKET,
    MINIO_REGION,
    MINIO_SSL,
)
from minio import Minio

import os

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
