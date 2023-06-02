"""

Copyright 2017-2023 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

import os
import sys
from importlib import import_module

import yaml

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Default settings file can come from environment, or default to root settings.yaml
SETTINGS_FILE = os.environ.get("SREGISTRY_SETTINGS_FILE") or os.path.join(
    BASE_DIR, "settings.yaml"
)

# Defaults across settings.
# These will be looked for in the environment with SREGISTRY_ prefix
# Each of these variables will be set to locals with the key name
BOOLEAN_DEFAULTS = {
    # Debug mode, typically useful for development
    "DEBUG": False,
    "API_REQUIRE_AUTH": False,
    # Which social auths do you want to use?
    "ENABLE_GOOGLE_AUTH": False,
    "ENABLE_TWITTER_AUTH": False,
    "ENABLE_GITHUB_AUTH": True,
    "ENABLE_GITLAB_AUTH": False,
    "ENABLE_BITBUCKET_AUTH": False,
    "ENABLE_GITHUB_ENTERPRISE_AUTH": False,
    "USER_COLLECTIONS": True,
    # Should registries by default be private, with no option for public?
    "PRIVATE_ONLY": False,
    # Should the default for a new registry be private or public?
    "DEFAULT_PRIVATE": False,
    # Disable all pushes of containers, recipes, etc. Also for Google Cloud Build
    "DISABLE_BUILDING": False,
    # A global setting to disable all webhooks / interaction with Github
    "DISABLE_GITHUB": False,
    # prevent responses from being received from Google Cloud Build
    "DISABLE_BUILD_RECEIVE": False,
    # use SSL for minio
    "MINIO_SSL": False,
    "MINIO_MULTIPART_UPLOAD": True,
    # Don't clean up images in Minio that are no longer referenced by sregistry
    "DISABLE_MINIO_CLEANUP": False,
    # Do you want to save complete response metadata per each pull?
    # If you disable, we still keep track of collection pull counts, but not specific versions
    "LOGGING_SAVE_RESPONSES": True,
    # Given that someone goes over, are they blocked for the period?
    "VIEW_RATE_LIMIT_BLOCK": True,
    # If using bitbucket, only allow verified emails
    "SOCIAL_AUTH_BITBUCKET_OAUTH2_VERIFIED_EMAILS_ONLY": None,  # True
}

STRING_DEFAULTS = {
    # Will be converted to list, and defaults to "*"
    "ALLOWED_HOSTS": None,
    "SECRET_KEY": "12345",
    "API_VERSION": "v1",
    "API_ANON_THROTTLE_RATE": "100/day",
    "API_USER_THROTTLE_RATE": "1000/day",
    "API_DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
    "API_DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "SOCIAL_AUTH_LOGIN_REDIRECT_URL": "http://127.0.0.1",
    # On any admin or plugin login redirect to standard social-auth entry point for agreement to terms
    "LOGIN_REDIRECT_URL": "/login",
    # DOMAIN NAMES
    ## IMPORTANT: if/when you switch to https, you need to change "DOMAIN_NAME"
    # to have https, otherwise some functionality will not work (e.g., GitHub webhooks)
    "DOMAIN_NAME": "http://127.0.0.1",
    "DOMAIN_NAME_HTTP": "http://127.0.0.1",
    # Get additional admins from the environment
    "HELP_CONTACT_EMAIL": "vsoch@users.noreply.github.com",
    "HELP_INSTITUTION_SITE": "https://srcc.stanford.edu",
    "REGISTRY_NAME": "Tacosaurus Computing Center",
    "REGISTRY_URI": "taco",
    "GOOGLE_ANALYTICS": "",  # "UA-XXXXXXXXX"  (leave this as empty string so it is set!)
    "DATABASE_ENGINE": "django.db.backends.postgresql_psycopg2",
    "DATABASE_NAME": "postgres",
    "DATABASE_USER": "postgres",
    "DATABASE_HOST": "db",
    "DATABASE_PORT": "5432",
    # Redis
    "REDIS_HOST": "redis",
    "REDIS_URL": "redis://redis/0",
    # Minio Storage
    "MINIO_ROOT_USER": None,
    "MINIO_ROOT_PASSWORD": None,
    "MINIO_SERVER": "minio:9000",  # Internal to sregistry
    "MINIO_EXTERNAL_SERVER": "127.0.0.1:9000",  # minio server for Singularity to interact with
    "MINIO_BUCKET": "sregistry",
    "MINIO_REGION": "us-east-1",
    # The rate limit for each view, django-ratelimit, "50 per day per ipaddress)
    "VIEW_RATE_LIMIT": "50/1d",
    "DJANGO_LOG_LEVEL": "WARNING",
    # An image url or one of the following: 'mm', 'identicon', 'monsterid', 'wavatar', 'retro'. Defaults to 'mm', and 'retro' here
    "GRAVATAR_DEFAULT_IMAGE": "retro",
    # Twitter Social Authentication
    "SOCIAL_AUTH_TWITTER_KEY": None,
    "SOCIAL_AUTH_TWITTER_SECRET": None,
    # Google social authentication
    # http://psa.matiasaguirre.net/docs/backends/google.html?highlight=google
    "SOCIAL_AUTH_GOOGLE_OAUTH2_KEY": None,  # 'xxxxxxxxxxxxxxxxxx.apps.googleusercontent.com'
    "SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET": None,
    # Google social authentication
    # http://psa.matiasaguirre.net/docs/backends/github.html?highlight=github
    "SOCIAL_AUTH_GITHUB_KEY": None,
    "SOCIAL_AUTH_GITHUB_SECRET": None,
    # GitHub Enterprise
    "SOCIAL_AUTH_GITHUB_ENTERPRISE_URL": None,
    # Set the API URL for your GitHub Enterprise appliance:
    "SOCIAL_AUTH_GITHUB_ENTERPRISE_API_URL": None,
    # Fill the Client ID and Client Secret values from GitHub in the settings
    "SOCIAL_AUTH_GITHUB_ENTERPRISE_KEY": None,
    "SOCIAL_AUTH_GITHUB_ENTERPRISE_SECRET": None,
    # GitLab OAuth2
    "SOCIAL_AUTH_GITLAB_KEY": None,
    "SOCIAL_AUTH_GITLAB_SECRET": None,
    # Google Cloud Build + Storage: configure a custom builder and storage endpoint
    "GOOGLE_APPLICATION_CREDENTIALS": None,  # /path/to/credentials.json
    "GOOGLE_PROJECT": None,
    # After build, do not delete intermediate dependencies in cloudbuild bucket (keep them as cache for rebuild if needed).
    # Defaults to being unset, meaning that files are cleaned up. If you define this as anything, the build files will be cached.
    "GOOGLE_BUILD_CACHE": None,  # "true"
    # if you want to specify a version of Singularity. The version must coincide with a container tag hosted under singularityware/singularity.
    # The version will default to 3.2.0-slim If you want to use a different version, update this variable.
    "GOOGLE_BUILD_SINGULARITY_VERSION": None,  # "v3.2.1-slim"
    # is the name for the bucket you want to create. The example here is using the unique identifier appended with “sregistry-"
    # If you don't define it, it will default to a string that includes the hostname.
    # Additionally, a temporary bucket is created with the same name ending in _cloudbuild. This bucket is for build time dependencies,
    # and is cleaned up after the fact. If you are having trouble getting a bucket it is likely because the name is taken,
    # and we recommend creating both <name> and <name>_cloudbuild in the console and then setting the name here.
    "GOOGLE_STORAGE_BUCKET": None,  # taco-singularity-registry"
    # Bitbucket social auth
    "SOCIAL_AUTH_BITBUCKET_OAUTH2_KEY": None,  # '<your-consumer-key>'
    "SOCIAL_AUTH_BITBUCKET_OAUTH2_SECRET": None,  # '<your-consumer-secret>'
    # LDAP Authentication (ldap-auth)
    # Only required if 'ldap-auth' is added to PLUGINS_ENABLED in config.py
    # This example assumes you are using an OpenLDAP directory
    # If using an alternative directory - e.g. Microsoft AD, 389 you
    # will need to modify attribute names/mappings accordingly
    # See https://django-auth-ldap.readthedocs.io/en/1.2.x/index.html
    # The URI to our LDAP server (may be ldap:// or ldaps://)
    "AUTH_LDAP_SERVER_URI": None,  # "ldaps://ldap.example.com
    # DN and password needed to bind to LDAP to retrieve user information
    # Can leave blank if anonymous binding is sufficient
    "AUTH_LDAP_BIND_DN": "",
    "AUTH_LDAP_BIND_PASSWORD": "",
    "AUTH_LDAP_USER_SEARCH": None,  # "ou=users,dc=example,dc=com"
    "AUTH_LDAP_GROUP_SEARCH": None,  # "ou=groups,dc=example,dc=com"
    # Anyone in this group can get a token to manage images, not superuser
    "AUTH_LDAP_STAFF_GROUP_FLAGS": None,  # "cn=staff,ou=django,ou=groups,dc=example,dc=com",
    # Anyone in this group is a superuser for the app
    "AUTH_LDAP_SUPERUSER_GROUP_FLAGS": None,  # "cn=superuser,ou=django,ou=groups,dc=example,dc=com"
    # Globus Assocation (globus)
    # Only required if 'globus' is added to PLUGINS_ENABLED in config.py
    "SOCIAL_AUTH_GLOBUS_KEY": None,
    "SOCIAL_AUTH_GLOBUS_USERNAME": None,  # "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@clients.auth.globus.org"
    "SOCIAL_AUTH_GLOBUS_SECRET": None,
    "GLOBUS_ENDPOINT_ID": None,
    # SAML Authentication (saml)
    # Only required if 'saml_auth' is added to PLUGINS_ENABLED
    "AUTH_SAML_IDP": None,  # "stanford"
    "AUTH_SAML_INSTITUTION": None,  # "Stanford University"
}

INTEGER_DEFAULTS = {
    "API_PAGE_SIZE": 10,
    # Set this to be some size in MB to limit uploads.
    # Uploads > 2.5GB will not use memory, but the filesystem
    "DATA_UPLOAD_MAX_MEMORY_SIZE": None,
    # Limit users to N collections (None is unlimited)
    "USER_COLLECTION_LIMIT": 2,
    # The number of collections to show on the /<domain>/collections page
    "COLLECTIONS_VIEW_PAGE_COUNT": 250,
    # The maximum number of downloads allowed per container/collection, per week
    "CONTAINER_WEEKLY_GET_LIMIT": 100,
    "COLLECTION_WEEKLY_GET_LIMIT": 100,
    "MINIO_SIGNED_URL_EXPIRE_MINUTES": 5,
    # Google Build
    # To prevent denial of service attacks on Google Cloud Storage, you should set a reasonable limit for the number of active, concurrent builds.
    # This number should be based on your expected number of users, repositories, and recipes per repository.
    "GOOGLE_BUILD_LIMIT": None,  # 100
    # The number of seconds for the build to timeout. If set to None, will be 10 minutes. If
    # unset, will default to 3 hours. This time should be less than the GOOGLE_BUILD_EXPIRE_SECONDS
    "GOOGLE_BUILD_TIMEOUT_SECONDS": None,
    # The number of seconds for the build to expire, meaning it's response is no longer accepted by the server. This must be defined.
    # Using 28800 would indicate 8 hours (in seconds)
    "GOOGLE_BUILD_EXPIRE_SECONDS": None,  # 28800
    # The number of seconds to expire a signed URL given to download a container
    # from storage. This can be much smaller than 10, as we only need it to endure
    # for the POST.
    "CONTAINER_SIGNED_URL_EXPIRE_SECONDS": None,  # 10
}

LIST_DEFAULTS = {
    #list the scopes that will be needed by the gitlab OAuth provider
    "SOCIAL_AUTH_GITLAB_SCOPE": [],

    # Plugins
    # Add the name of a plugin under shub.plugins here to enable it

    # Available Plugins:

    # - ldap_auth: Allows sregistry to authenticate against an LDAP directory
    # - google_build: a custom storage with that uses Google Cloud Build + Storage
    # - pam_auth: Allow users from (docker) host to log in
    # - globus: allows connection from sregistry to endpoints
    # - saml_auth: authentication with SAML
    # - pgp: deploy a key server alongside your registry

    "PLUGINS_ENABLED": [
        #    'pgp'
        #    'ldap_auth',
        #    'google_build'
        #    'pam_auth',
        #    'globus',
        #    'saml_auth'
    ]
}

# Environment helpers


def get_sregistry_envar(key):
    envar_key = "SREGISTRY_%s" % key
    return os.environ.get(envar_key)


def get_sregistry_envar_list(key):
    key = "SREGISTRY_%s" % key
    envar_list = os.environ.get(key) or []
    if envar_list:
        envar_list = [x.strip() for x in envar_list.split(",") if x.strip()]
    return envar_list


# Set boolean defaults from environment
for key in BOOLEAN_DEFAULTS:
    value = get_sregistry_envar(key)

    if value is None:
        continue

    # Setting a boolean
    if value.lower() in ["true", "1"]:
        BOOLEAN_DEFAULTS[key] = True

    elif value.lower() in ["false", "0"]:
        BOOLEAN_DEFAULTS[key] = False

    # Assume a boolean value incorrectly set is not intentional
    else:
        sys.exit("There was an issue setting %s as a boolean." % key)

# Set Integer values from the environment
for key in INTEGER_DEFAULTS:
    value = get_sregistry_envar(key)
    if value is not None:
        try:
            INTEGER_DEFAULTS[key] = int(value)
        except ValueError:
            sys.exit("There was an issue setting %s as an integer." % key)

# Set string environment variables
for key in STRING_DEFAULTS:
    value = get_sregistry_envar(key)
    if value is not None:
        STRING_DEFAULTS[key] = value


for key in LIST_DEFAULTS:
    value = get_sregistry_envar_list(key)
    if value is not []:
        LIST_DEFAULTS[key] = list(set(value))

# Finally, create settings object
class Settings:
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            setattr(self, key, value)

    def __str__(self):
        return "[sregistry-settings]"

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        for key, value in self.__dict__.items():
            yield key, value


DEFAULTS = STRING_DEFAULTS | BOOLEAN_DEFAULTS | INTEGER_DEFAULTS | LIST_DEFAULTS

# If we have a settings file, it takes preference to DEFAULTS
if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "r") as fd:
        custom_settings = yaml.load(fd.read(), Loader=yaml.FullLoader)
    for k, v in custom_settings.items():
        # Only update if it's set in the settings file.
        if v is None:
            continue
        DEFAULTS[k] = v

cfg = Settings(DEFAULTS)

# Application Programming Interface

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": cfg.API_DEFAULT_SCHEMA_CLASS,
    "DEFAULT_PAGINATION_CLASS": cfg.API_DEFAULT_PAGINATION_CLASS,
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ),
    # You can also customize the throttle rates, for anon and users
    "DEFAULT_THROTTLE_CLASSES": ("rest_framework.throttling.AnonRateThrottle",),
    # https://www.django-rest-framework.org/api-guide/throttling/
    "DEFAULT_THROTTLE_RATES": {
        "anon": cfg.API_ANON_THROTTLE_RATE,
        "user": cfg.API_USER_THROTTLE_RATE,
    },
    "PAGE_SIZE": cfg.API_PAGE_SIZE,
}

# You can require authentication for your API
if DEFAULTS["API_REQUIRE_AUTH"]:
    REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = (
        "rest_framework.permissions.IsAuthenticated",
    )

# Applications

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sitemaps",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_user_agents",
    "shub.apps.api",
    "shub.apps.base",
    "shub.apps.logs",
    "shub.apps.main",
    "shub.apps.users",
    "shub.apps.singularity",
    "shub.apps.library",
]

THIRD_PARTY_APPS = [
    "social_django",
    "crispy_forms",
    "django_rq",
    "django_gravatar",
    "django_extensions",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_swagger",
    "taggit",
]


INSTALLED_APPS += THIRD_PARTY_APPS


# Authentication

# Python-social-auth

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "social_core.backends.username.UsernameAuth",
    "social_core.backends.open_id.OpenIdAuth",
    "social_core.backends.saml.SAMLAuth",
    "social_core.backends.google.GoogleOAuth2",
    "social_core.backends.twitter.TwitterOAuth",
    "social_core.backends.facebook.FacebookOAuth2",
    "shub.apps.users.views.auth.ShubGithubOAuth2",
    # "social_core.backends.github.GithubOAuth2",
    "social_core.backends.github_enterprise.GithubEnterpriseOAuth2",
    "social_core.backends.gitlab.GitLabOAuth2",
    "social_core.backends.bitbucket.BitbucketOAuth2",
)


SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "shub.apps.users.views.social_user",
    "shub.apps.users.views.redirect_if_no_refresh_token",
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.social_auth.associate_by_email",  # <--- must share same email
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
)


# If these need to be exposed via envar, we can do (they aren't currently used)
# http://psa.matiasaguirre.net/docs/configuration/settings.html#urls-options
# SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
# SOCIAL_AUTH_USER_MODEL = 'django.contrib.auth.models.User'
# SOCIAL_AUTH_STORAGE = 'social.apps.django_app.me.models.DjangoStorage'
# SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
# SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/logged-in/'
# SOCIAL_AUTH_LOGIN_ERROR_URL = '/login-error/'
# SOCIAL_AUTH_LOGIN_URL = '/login-url/'
# SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/new-users-redirect-url/'
# SOCIAL_AUTH_LOGIN_REDIRECT_URL
# SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = '/new-association-redirect-url/'
# SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = '/account-disconnected-redirect-url/'
# SOCIAL_AUTH_INACTIVE_USER_URL = '/inactive-user/'


# AUTHENTICATION

DOMAIN_NAKED = cfg.DOMAIN_NAME_HTTP.replace("http://", "")

envar_admins = get_sregistry_envar_list("ADMINS")
ADMINS = (("vsochat", "@vsoch"),)
if envar_admins:
    ADMINS = tuple(envar_admins)
MANAGERS = ADMINS


# DATABASE

# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": cfg.DATABASE_ENGINE,
        "NAME": cfg.DATABASE_NAME,
        "USER": cfg.DATABASE_USER,
        "HOST": cfg.DATABASE_HOST,
        "PORT": cfg.DATABASE_PORT,
    }
}

# STORAGE

MINIO_ROOT_USER = os.environ.get("MINIO_ROOT_USER") or cfg.MINIO_ROOT_USER
MINIO_ROOT_PASSWORD = os.environ.get("MINIO_ROOT_PASSWORD") or cfg.MINIO_ROOT_PASSWORD

# Default Django logging is WARNINGS+ to console
# so visible via docker-compose logs uwsgi
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": cfg.DJANGO_LOG_LEVEL,
        }
    },
}


# Custom user model (unlikely to change)
AUTH_USER_MODEL = "users.User"
SOCIAL_AUTH_USER_MODEL = "users.User"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Allow setting custom hosts in the environment
ALLOWED_HOSTS = cfg.ALLOWED_HOSTS or ["*"]
if not isinstance(ALLOWED_HOSTS, list):
    ALLOWED_HOSTS = [ALLOWED_HOSTS]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "shub.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
                "shub.apps.base.context_processors.auth_processor",
                "shub.apps.base.context_processors.domain_processor",
                "shub.apps.base.context_processors.settings_processor",
                "shub.apps.base.context_processors.help_processor",  # custom context processors
            ]
        },
    }
]


TEMPLATES[0]["OPTIONS"]["debug"] = cfg.DEBUG
WSGI_APPLICATION = "shub.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = "en-us"
# TIME_ZONE = 'America/Chicago'
USE_I18N = True
USE_L10N = True
USE_TZ = True

SESSION_SERIALIZER = "django.contrib.sessions.serializers.PickleSerializer"
SENDFILE_BACKEND = "sendfile.backends.development"
PRIVATE_MEDIA_REDIRECT_HEADER = "X-Accel-Redirect"
CRISPY_TEMPLATE_PACK = "bootstrap3"

CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

MEDIA_ROOT = "/var/www/images"
MEDIA_URL = "/images/"
STATIC_ROOT = "/var/www/static"
STATIC_URL = "/static/"
UPLOAD_PATH = "%s/_upload" % MEDIA_ROOT


RQ_QUEUES = {"default": {"URL": cfg.REDIS_URL}}
RQ = {"host": cfg.REDIS_HOST, "db": 0}



# Finally, ensure all variables in cfg are set in locals
for key, value in cfg:
    # Don't set if the value is empty, or it's been set previously
    if value is None or key in locals() and locals()[key] is not None:
        continue
    locals()[key] = value


# Plugins

# If PAM_AUTH in plugins enbled, add django_pam
if "pam_auth" in PLUGINS_ENABLED:
    INSTALLED_APPS += ["django_pam"]

# If LDAP_AUTH in plugins enabled, populate from settings
if "ldap_auth" in PLUGINS_ENABLED:
    # To work with OpenLDAP and posixGroup groups we need to import some things
    import ldap
    from django_auth_ldap.config import LDAPSearch, PosixGroupType

    # DN and password needed to bind to LDAP to retrieve user information
    # Can leave blank if anonymous binding is sufficient
    AUTH_LDAP_BIND_DN = cfg.AUTH_LDAP_BIND_DN or ""
    AUTH_LDAP_BIND_PASSWORD = cfg.AUTH_LDAP_BIND_PASSWORD or ""

    # Any user account that has valid auth credentials can login
    AUTH_LDAP_USER_SEARCH = LDAPSearch(
        cfg.AUTH_LDAP_USER_SEARCH, ldap.SCOPE_SUBTREE, "(uid=%(user)s)"
    )
    AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
        cfg.AUTH_LDAP_GROUP_SEARCH, ldap.SCOPE_SUBTREE, "(objectClass=posixGroup)"
    )
    AUTH_LDAP_GROUP_TYPE = PosixGroupType()

    # Populate the Django user model from the LDAP directory.
    AUTH_LDAP_USER_ATTR_MAP = {
        "first_name": "givenName",
        "last_name": "sn",
        "email": "mail",
    }

    # Map LDAP group membership into Django admin flags
    AUTH_LDAP_USER_FLAGS_BY_GROUP = {
        # Anyone in this group can get a token to manage images, not superuser
        "is_staff": cfg.AUTH_LDAP_STAFF_GROUP_FLAGS,
        # Anyone in this group is a superuser for the app
        "is_superuser": cfg.AUTH_LDAP_SUPERUSER_GROUP_FLAGS,
    }


# If google_build in use, we are required to include GitHub
if "google_build" in PLUGINS_ENABLED:
    # For task discovery by celery
    SOCIAL_AUTH_GITHUB_SCOPE = [
        "admin:repo_hook",
        "repo:status",
        "user:email",
        "read:org",
        "admin:org_hook",
        "deployment_status",
    ]
    ENABLE_GITHUB_AUTH = True

# Apply any plugin settings
for plugin in PLUGINS_ENABLED:
    plugin_module = "shub.plugins." + plugin
    plugin = import_module(plugin_module)

    # Add the plugin to INSTALLED APPS
    INSTALLED_APPS.append(plugin_module)

    # Add AUTHENTICATION_BACKENDS if defined, for authentication plugins
    if hasattr(plugin, "AUTHENTICATION_BACKENDS"):
        AUTHENTICATION_BACKENDS = (
            AUTHENTICATION_BACKENDS + plugin.AUTHENTICATION_BACKENDS
        )

    # Add custom context processors, if defines for plugin
    if hasattr(plugin, "CONTEXT_PROCESSORS"):
        for context_processor in plugin.CONTEXT_PROCESSORS:
            TEMPLATES[0]["OPTIONS"]["context_processors"].append(context_processor)

# Try reading in from secrets first (no issue if not found)
try:
    from .secrets import *  # noqa
except ImportError:
    pass

if not MINIO_ROOT_USER or not MINIO_ROOT_PASSWORD:
    print(
        "Warning: either MINIO_ROOT_USER or MINIO_ROOT_PASSWORD is missing, storage may not work."
    )

# If we don't have a secret key, no go
if (
    "SECRET_KEY" not in locals()
    or "SECRET_KEY" in locals()
    and not locals()["SECRET_KEY"]
):
    sys.exit("SECRET_KEY is required but not set. Set SREGISTRY_SECRET_KEY.")


if ENABLE_GOOGLE_AUTH:  # noqa
    # The scope is not needed, unless you want to develop something new.
    SOCIAL_AUTH_GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {
        "access_type": "offline",
        "approval_prompt": "auto",
    }
