"""

Copyright (C) 2017-2022 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from importlib import import_module
import yaml
import os

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
    "API_REQUIRE_AUTH": False,
    # Which social auths do you want to use?
    "ENABLE_GOOGLE_AUTH": False,
    "ENABLE_TWITTER_AUTH": False,
    "ENABLE_GITHUB_AUTH": True,
    "ENABLE_GITLAB_AUTH": False,
    "ENABLE_BITBUCKET_AUTH": False,
    "ENABLE_GITHUB_ENTERPRISE_AUTH": False,
    # NOTE you will need to set authentication methods up.
    # Configuration goes into secrets.py
    # see https://singularityhub.github.io/sregistry/install.html
    # secrets.py.example provides a template to work from
    # Allow users to create public collections
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
}

STRING_DEFAULTS = {
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
    # "UA-XXXXXXXXX"
    "GOOGLE_ANALYTICS": None,
    "GOOGLE_BUILD_SINGULARITY_VERSION": "v3.3.0-slim",
    "SREGISTRY_DATABASE_ENGINE": "django.db.backends.postgresql_psycopg2",
    "SREGISTRY_DATABASE_NAME": "postgres",
    "SREGISTRY_DATABASE_USER": "postgres",
    "SREGISTRY_DATABASE_HOST": "db",
    "SREGISTRY_DATABASE_PORT": "5432",
    # Minio Storage
    "MINIO_SERVER": "minio:9000",  # Internal to sregistry
    "MINIO_EXTERNAL_SERVER": "127.0.0.1:9000",  # minio server for Singularity to interact with
    "MINIO_BUCKET": "sregistry",
    "MINIO_REGION": "us-east-1",
    # The rate limit for each view, django-ratelimit, "50 per day per ipaddress)
    "VIEW_RATE_LIMIT": "50/1d",
    "DJANGO_LOG_LEVEL": "WARNING",
    # An image url or one of the following: 'mm', 'identicon', 'monsterid', 'wavatar', 'retro'. Defaults to 'mm'
    "GRAVATAR_DEFAULT_IMAGE": "retro",
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
    "GOOGLE_BUILD_LIMIT": 100,
    "GOOGLE_BUILD_TIMEOUT_SECONDS": None,  # None defaults to 10 minutes
    "GOOGLE_BUILD_EXPIRE_SECONDS": 28800,
    "CONTAINER_SIGNED_URL_EXPIRE_SECONDS": 10,
    "MINIO_SIGNED_URL_EXPIRE_MINUTES": 5,
}

# Environment helpers


def get_sregistry_envar(key):
    envar_key = "SREGISTRY_%s" % key
    return os.environ.get(envar_key)


def get_sregistry_envar_list(key):
    envar_list = os.environ.get(key) or []
    if envar_list:
        envar_list = [x.strip() for x in envar_list.split(",") if x.strip()]
    return envar_list


# Try reading in from secrets first
try:
    from .secrets import *

# Fallback to dummy secrets (usually for testing)
except ImportError:
    from .dummy_secrets import *

    pass


# Set boolean defaults from environment
for key in BOOLEAN_DEFAULTS:
    value = get_sregistry_envar(key)

    if not value:
        continue

    # Setting a boolean
    if value.lower() == "true":
        BOOLEAN_DEFAULTS[key] = True

    elif value.lower() == "false":
        BOOLEAN_DEFAULTS[key] = False

# Set Integer values from the environment
for key in INTEGER_DEFAULTS:
    value = get_sregistry_envar(key)
    if value:
        try:
            INTEGER_DEFAULTS[key] = int(value)
        except:
            print("There was an issue setting %s as an integer." % key)

# Set string environment variables
for key in STRING_DEFAULTS:
    value = get_sregistry_envar(key)
    if value:
        STRING_DEFAULTS[key] = value

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


DEFAULTS = STRING_DEFAULTS | BOOLEAN_DEFAULTS | INTEGER_DEFAULTS

# If we have a settings file, it takes preference to DEFAULTS
if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "r") as fd:
        custom_settings = yaml.load(fd.read(), Loader=yaml.FullLoader)
    DEFAULTS = DEFAULTS.update(custom_settings)

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


# If these need to be exposed via envar, we can do.
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

envar_admins = get_sregistry_envar_list("SREGISTRY_ADMINS")
ADMINS = (("vsochat", "@vsoch"),)
if envar_admins:
    ADMINS = tuple(envar_admins)
MANAGERS = ADMINS


# DATABASE

# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": cfg.SREGISTRY_DATABASE_ENGINE,
        "NAME": cfg.SREGISTRY_DATABASE_NAME,
        "USER": cfg.SREGISTRY_DATABASE_USER,
        "HOST": cfg.SREGISTRY_DATABASE_HOST,
        "PORT": cfg.SREGISTRY_DATABASE_PORT,
    }
}

# STORAGE

MINIO_ROOT_USER = os.environ.get("MINIO_ROOT_USER")
MINIO_ROOT_PASSWORD = os.environ.get("MINIO_ROOT_PASSWORD")

if not MINIO_ROOT_USER or not MINIO_ROOT_PASSWORD:
    print(
        "Warning: either MINIO_ROOT_USER or MINIO_ROOT_PASSWORD is missing, storage may not work."
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

ALLOWED_HOSTS = ["*"]


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


TEMPLATES[0]["OPTIONS"]["debug"] = True
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


RQ_QUEUES = {"default": {"URL": os.getenv("REDIS_URL", "redis://redis/0")}}

RQ = {"host": "redis", "db": 0}

# background tasks
BACKGROUND_TASK_RUN_ASYNC = True

# Plugins

# If PAM_AUTH in plugins enbled, add django_pam
if "pam_auth" in PLUGINS_ENABLED:
    INSTALLED_APPS += ["django_pam"]

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

# Finally, ensure all variables in cfg are set in locals
for key, value in cfg:
    locals()[key] = value

# Add SREGISTRY_SECRET_ from the environment
for key, value in os.environ.items():
    if key.startswith("SREGISTRY_SECRET_"):
        secret_key = key.replace("SREGISTRY_SECRET_", "")
        if not value:
            continue
        if value.lower() == "true":
            value = True
        elif value.lower() == "false":
            value = False
        locals()[secret_key] = value
