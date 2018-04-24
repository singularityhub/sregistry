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

# AUTHENTICATION

# Which social auths do you want to use?
ENABLE_GOOGLE_AUTH=False
ENABLE_TWITTER_AUTH=True
ENABLE_GITHUB_AUTH=False
ENABLE_GITLAB_AUTH=False

# NOTE you will need to set autehtication methods up.
# Configuration goes into secrets.py
# see https://singularityhub.github.io/sregistry/install.html
# secrets.py.example provides a template to work from

# See below for additional authentication module, e.g. LDAP that are
# available, and configured, as plugins.



# DOMAIN NAMES

DOMAIN_NAME = "http://127.0.0.1"
DOMAIN_NAME_HTTP = "http://127.0.0.1"
DOMAIN_NAKED = DOMAIN_NAME_HTTP.replace('http://','')

ADMINS = (( 'vsochat', 'vsochat@gmail.com'),)
MANAGERS = ADMINS

HELP_CONTACT_EMAIL = 'vsochat@stanford.edu'
HELP_INSTITUTION_SITE = 'srcc.stanford.edu'
REGISTRY_NAME = "Tacosaurus Computing Center"
REGISTRY_URI = "taco"



# PERMISSIONS

# Allow users to create public collections
USER_COLLECTIONS = True

# Should registries by default be private, with no option for public?
PRIVATE_ONLY = False

# Should the default for a new registry be private or public?
DEFAULT_PRIVATE = False



# DATABASE

# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db',
        'PORT': '5432',
    }
}


# Visualizations

# After how many single containers should we switch to showing collections
# only? >= 1000
VISUALIZATION_TREEMAP_COLLECTION_SWITCH=1000


# Logging

# Do you want to save complete response metadata per each pull?
# If you disable, we still keep track of collection pull counts, but not specific versions
LOGGING_SAVE_RESPONSES=True

# Plugins
# Add the name of a plugin under shub.plugins here to enable it



# Available Plugins:

# - ldap_auth: Allows sregistry to authenitcate against an LDAP directory
# - globus: allows connection from sregistry to endpoints

PLUGINS_ENABLED = [
#    'ldap_auth'
]
PLUGINS_ENABLED+=["globus"]
ROBOTNAME='crusty-malarkey-2922'
PLUGIN_GLOBUS_ENDPOINT="502635e0-4418-11e8-8e06-0a6d4e044368"
ROBOTNAME='sticky-blackbean-9783'
PLUGIN_GLOBUS_ENDPOINT="ba5b80c2-4798-11e8-8ee0-0a6d4e044368"
