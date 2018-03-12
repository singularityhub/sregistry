'''

Copyright (C) 2017-2018 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017-2018 Vanessa Sochat.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

'''


from shub.settings import ( 
    DOMAIN_NAME,
    DOMAIN_NAKED,
    ENABLE_GOOGLE_AUTH,
    ENABLE_TWITTER_AUTH,
    ENABLE_GITHUB_AUTH,
    ENABLE_GITLAB_AUTH,
    ENABLE_FIWARE_AUTH,
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
            "ENABLE_FIWARE_AUTH":ENABLE_FIWARE_AUTH,
            "PLUGINS_ENABLED":PLUGINS_ENABLED,}


