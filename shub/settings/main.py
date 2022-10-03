"""

Copyright (C) 2017-2022 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Custom user model
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

# Gravatar
GRAVATAR_DEFAULT_IMAGE = "retro"
# An image url or one of the following: 'mm', 'identicon', 'monsterid', 'wavatar', 'retro'. Defaults to 'mm'
