"""

Copyright (C) 2017-2022 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

import os

# AUTHENTICATION

# Which social auths do you want to use?
ENABLE_GOOGLE_AUTH = False
ENABLE_TWITTER_AUTH = False
ENABLE_GITHUB_AUTH = True
ENABLE_GITLAB_AUTH = False
ENABLE_BITBUCKET_AUTH = False
ENABLE_GITHUB_ENTERPRISE_AUTH = False

# NOTE you will need to set authentication methods up.
# Configuration goes into secrets.py
# see https://singularityhub.github.io/sregistry/install.html
# secrets.py.example provides a template to work from

# See below for additional authentication module, e.g. LDAP that are
# available, and configured, as plugins.

# Environment helpers


def get_sregistry_envar(key):
    envar_key = "SREGISTRY_%s" % key
    return os.environ.get(envar_key)


def get_sregistry_envar_list(key):
    envar_list = os.environ.get(key) or []
    if envar_list:
        envar_list = [x.strip() for x in envar_list.split(",") if x.strip()]
    return envar_list


# DOMAIN NAMES
## IMPORTANT: if/when you switch to https, you need to change "DOMAIN_NAME"
# to have https, otherwise some functionality will not work (e.g., GitHub webhooks)

DOMAIN_NAME = "http://127.0.0.1"
DOMAIN_NAME_HTTP = "http://127.0.0.1"
DOMAIN_NAKED = DOMAIN_NAME_HTTP.replace("http://", "")

envar_admins = get_sregistry_envar_list("SREGISTRY_ADMINS")
ADMINS = (("vsochat", "@vsoch"),)
if envar_admins:
    ADMINS = tuple(envar_admins)
MANAGERS = ADMINS

# Get additional admins from the environment

HELP_CONTACT_EMAIL = "vsochat@stanford.edu"
HELP_INSTITUTION_SITE = "https://srcc.stanford.edu"
REGISTRY_NAME = "Tacosaurus Computing Center"
REGISTRY_URI = "taco"
GOOGLE_ANALYTICS = None  # "UA-XXXXXXXXX"

# Permissions and Views

# Set this to be some size in MB to limit uploads.
# Uploads > 2.5GB will not use memory, but the filesystem
DATA_UPLOAD_MAX_MEMORY_SIZE = None

# Allow users to create public collections
USER_COLLECTIONS = True

# Limit users to N collections (None is unlimited)
USER_COLLECTION_LIMIT = 2

# Should registries by default be private, with no option for public?
PRIVATE_ONLY = False

# Should the default for a new registry be private or public?
DEFAULT_PRIVATE = False

# The number of collections to show on the /<domain>/collections page
COLLECTIONS_VIEW_PAGE_COUNT = 250

# The maximum number of downloads allowed per container/collection, per week
CONTAINER_WEEKLY_GET_LIMIT = 100
COLLECTION_WEEKLY_GET_LIMIT = 100

# Disable all pushes of containers, recipes, etc. Also for Google Cloud Build
DISABLE_BUILDING = False

# Plugins ######################################################################
# See dummy_secrets.py for more details.

SREGISTRY_GOOGLE_BUILD_LIMIT = 100
SREGISTRY_GOOGLE_BUILD_SINGULARITY_VERSION = "v3.3.0-slim"
SREGISTRY_GOOGLE_BUILD_TIMEOUT_SECONDS = None  # None defaults to 10 minutes
SREGISTRY_GOOGLE_BUILD_EXPIRE_SECONDS = 28800
CONTAINER_SIGNED_URL_EXPIRE_SECONDS = 10

# A global setting to disable all webhooks / interaction with Github
DISABLE_GITHUB = False

# prevent responses from being received from Google Cloud Build
DISABLE_BUILD_RECEIVE = False


# DATABASE

# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SREGISTRY_DATABASE_ENGINE")
        or "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("SREGISTRY_DATABASE_NAME") or "postgres",
        "USER": os.environ.get("SREGISTRY_DATABASE_USER") or "postgres",
        "HOST": os.environ.get("SREGISTRY_DATABASE_HOST") or "db",
        "PORT": os.environ.get("SREGISTRY_DATABASE_PORT") or "5432",
    }
}

# STORAGE

MINIO_SERVER = "minio:9000"  # Internal to sregistry
MINIO_EXTERNAL_SERVER = (
    "127.0.0.1:9000"  # minio server for Singularity to interact with
)
MINIO_BUCKET = "sregistry"
MINIO_SSL = False  # use SSL for minio
MINIO_SIGNED_URL_EXPIRE_MINUTES = 5
MINIO_REGION = "us-east-1"
MINIO_MULTIPART_UPLOAD = True
MINIO_ROOT_USER = os.environ.get("MINIO_ROOT_USER")
MINIO_ROOT_PASSWORD = os.environ.get("MINIO_ROOT_PASSWORD")

if not MINIO_ROOT_USER or not MINIO_ROOT_PASSWORD:
    print(
        "Warning: either MINIO_ROOT_USER or MINIO_ROOT_PASSWORD is missing, storage may not work."
    )

# Don't clean up images in Minio that are no longer referenced by sregistry
DISABLE_MINIO_CLEANUP = False

# Logging

# Do you want to save complete response metadata per each pull?
# If you disable, we still keep track of collection pull counts, but not specific versions
LOGGING_SAVE_RESPONSES = True

# Rate Limits

VIEW_RATE_LIMIT = "50/1d"  # The rate limit for each view, django-ratelimit, "50 per day per ipaddress)
VIEW_RATE_LIMIT_BLOCK = (
    True  # Given that someone goes over, are they blocked for the period?
)

# Plugins
# Add the name of a plugin under shub.plugins here to enable it

# Available Plugins:

# - ldap_auth: Allows sregistry to authenticate against an LDAP directory
# - google_build: a custom storage with that uses Google Cloud Build + Storage
# - pam_auth: Allow users from (docker) host to log in
# - globus: allows connection from sregistry to endpoints
# - saml_auth: authentication with SAML
# - pgp: deploy a key server alongside your registry

PLUGINS_ENABLED = [
    #    'pgp'
    #    'ldap_auth',
    #    'google_build'
    #    'pam_auth',
    #    'globus',
    #    'saml_auth'
]

# Any plugins enabled from the environment?
PLUGINS_ENABLED += get_sregistry_envar_list("SREGISTRY_PLUGINS_ENABLED")

## Environment

# Custom additions are handled before this
# Limit defaults that user can set
BOOLEAN_DEFAULTS = [
    "ENABLE_GOOGLE_AUTH",
    "ENABLE_TWITTER_AUTH",
    "ENABLE_GITHUB_AUTH",
    "ENABLE_GITLAB_AUTH",
    "ENABLE_BITBUCKET_AUTH",
    "ENABLE_GITHUB_ENTERPRISE_AUTH",
    "USER_COLLECTIONS",
    "PRIVATE_ONLY",
    "DEFAULT_PRIVATE",
    "DISABLE_BUILDING",
    "SREGISTRY_GOOGLE_BUILD_SINGULARITY_VERSION",
    "DISABLE_GITHUB",
    "DISABLE_BUILD_RECEIVE",
    "MINIO_SSL",
    "MINIO_MULTIPART_UPLOAD",
    "DISABLE_MINIO_CLEANUP",
    "LOGGING_SAVE_RESPONSES",
    "VIEW_RATE_LIMIT_BLOCK",
]

STRING_DEFAULTS = [
    "DOMAIN_NAME",
    "DOMAIN_NAME_HTTP",
    "HELP_CONTACT_EMAIL",
    "HELP_INSTITUTION_SITE",
    "REGISTRY_NAME",
    "REGISTRY_URI",
    "GOOGLE_ANALYTICS",
    "MINIO_SERVER",
    "MINIO_EXTERNAL_SERVER",
    "MINIO_BUCKET",
    "MINIO_REGION",
    "VIEW_RATE_LIMIT",
]

INTEGER_DEFAULTS = [
    "DATA_UPLOAD_MAX_MEMORY_SIZE",
    "USER_COLLECTION_LIMIT",
    "COLLECTIONS_VIEW_PAGE_COUNT",
    "CONTAINER_WEEKLY_GET_LIMIT",
    "COLLECTION_WEEKLY_GET_LIMIT",
    "SREGISTRY_GOOGLE_BUILD_LIMIT",
    "SREGISTRY_GOOGLE_BUILD_TIMEOUT_SECONDS",
    "SREGISTRY_GOOGLE_BUILD_EXPIRE_SECONDS",
    "CONTAINER_SIGNED_URL_EXPIRE_SECONDS",
    "MINIO_SIGNED_URL_EXPIRE_MINUTES",
]

# Set envars by type
for key in BOOLEAN_DEFAULTS:
    value = get_sregistry_envar(key)

    # Setting a boolean
    if value in ["true", "True"]:
        locals()[key] = True
        print("Setting %s from the environment to True" % key)

    elif value in ["False", "false"]:
        locals()[key] = False
        print("Setting %s from the environment to False" % key)

# Integer values
for key in INTEGER_DEFAULTS:
    value = get_sregistry_envar(key)
    if value:
        try:
            locals()[key] = int(value)
        except:
            print("There was an issue setting %s as an integer." % key)

# Set string environment variables
for key in STRING_DEFAULTS:
    value = get_sregistry_envar(key)

    if value:
        print("Setting %s from the environment." % key)
        locals()[key] = value
