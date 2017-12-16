'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017 Vanessa Sochat.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''


from shub.settings import ( 
    DOMAIN_NAME,
    DOMAIN_NAKED,
    ENABLE_GOOGLE_AUTH,
    ENABLE_TWITTER_AUTH,
    ENABLE_GITHUB_AUTH,
    ENABLE_GITLAB_AUTH,
    HELP_CONTACT_EMAIL,
    HELP_INSTITUTION_SITE,
    PRIVATE_ONLY,
    REGISTRY_URI,
    REGISTRY_NAME,
    PLUGINS_ENABLED,
)

def domain_processor(request):
    return {'domain': DOMAIN_NAME,
            'DOMAIN_NAKED':DOMAIN_NAKED,
            'REGISTRY_URI': REGISTRY_URI,
            'REGISTRY_NAME':REGISTRY_NAME }


def help_processor(request):
    return {'HELP_CONTACT_EMAIL': HELP_CONTACT_EMAIL,
            'HELP_INSTITUTION_SITE':HELP_INSTITUTION_SITE}

def settings_processor(request):
    return {'PRIVATE_ONLY':PRIVATE_ONLY }


def auth_processor(request):
    return {"ENABLE_GOOGLE_AUTH":ENABLE_GOOGLE_AUTH,
            "ENABLE_TWITTER_AUTH":ENABLE_TWITTER_AUTH,
            "ENABLE_GITHUB_AUTH":ENABLE_GITHUB_AUTH,
            "ENABLE_GITLAB_AUTH":ENABLE_GITLAB_AUTH,
            "PLUGINS_ENABLED":PLUGINS_ENABLED,}


