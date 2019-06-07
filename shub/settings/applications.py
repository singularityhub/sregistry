'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_user_agents',
    'shub.apps.api',
    'shub.apps.base',
    'shub.apps.logs',
    'shub.apps.main',
    'shub.apps.users',
    'shub.apps.singularity'
]

THIRD_PARTY_APPS = [
    'social_django',
    'crispy_forms',
    'django_gravatar',
    'django_extensions',
    'djcelery',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_swagger',
    'taggit',
]


INSTALLED_APPS += THIRD_PARTY_APPS
