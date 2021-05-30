"""

Copyright (C) 2017-2021 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.conf import settings


def domain_processor(request):
    return {
        "domain": settings.DOMAIN_NAME,
        "DOMAIN_NAKED": settings.DOMAIN_NAKED,
        "REGISTRY_URI": settings.REGISTRY_URI,
        "REGISTRY_NAME": settings.REGISTRY_NAME,
        "GOOGLE_ANALYTICS": settings.GOOGLE_ANALYTICS,
    }


def help_processor(request):
    return {
        "HELP_CONTACT_EMAIL": settings.HELP_CONTACT_EMAIL,
        "HELP_INSTITUTION_SITE": settings.HELP_INSTITUTION_SITE,
    }


def settings_processor(request):
    return {"PRIVATE_ONLY": settings.PRIVATE_ONLY}


def auth_processor(request):
    return {
        "ENABLE_GOOGLE_AUTH": settings.ENABLE_GOOGLE_AUTH,
        "ENABLE_TWITTER_AUTH": settings.ENABLE_TWITTER_AUTH,
        "ENABLE_GITHUB_AUTH": settings.ENABLE_GITHUB_AUTH,
        "ENABLE_GITHUB_ENTERPRISE_AUTH": settings.ENABLE_GITHUB_ENTERPRISE_AUTH,
        "ENABLE_GITLAB_AUTH": settings.ENABLE_GITLAB_AUTH,
        "ENABLE_BITBUCKET_AUTH": settings.ENABLE_BITBUCKET_AUTH,
        "PLUGINS_ENABLED": settings.PLUGINS_ENABLED,
    }
