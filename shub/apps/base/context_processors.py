'''

Copyright (C) 2017-2019 Vanessa Sochat.

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

from django.conf import settings

def domain_processor(request):
    return {'domain': settings.DOMAIN_NAME,
            'DOMAIN_NAKED':settings.DOMAIN_NAKED,
            'REGISTRY_URI': settings.REGISTRY_URI,
            'REGISTRY_NAME': settings.REGISTRY_NAME}


def help_processor(request):
    return {'HELP_CONTACT_EMAIL': settings.HELP_CONTACT_EMAIL,
            'HELP_INSTITUTION_SITE': settings.HELP_INSTITUTION_SITE}

def settings_processor(request):
    return {'PRIVATE_ONLY': settings.PRIVATE_ONLY }


def auth_processor(request):
    return {"ENABLE_GOOGLE_AUTH": settings.ENABLE_GOOGLE_AUTH,
            "ENABLE_TWITTER_AUTH": settings.ENABLE_TWITTER_AUTH,
            "ENABLE_GITHUB_AUTH": settings.ENABLE_GITHUB_AUTH,
            "ENABLE_GITLAB_AUTH": settings.ENABLE_GITLAB_AUTH,
            "PLUGINS_ENABLED": settings.PLUGINS_ENABLED}


