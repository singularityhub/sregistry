'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017 Vanessa Sochat.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

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

DOMAIN_NAME = "http://127.0.0.1"
DOMAIN_NAME_HTTP = "http://127.0.0.1"
DOMAIN_NAKED = DOMAIN_NAME_HTTP.replace('http://','')

ADMINS = (( 'vsochat', 'vsochat@gmail.com'),)
MANAGERS = ADMINS

HELP_CONTACT_EMAIL = 'vsochat@stanford.edu'
HELP_INSTITUTION_SITE = 'srcc.stanford.edu'
REGISTRY_NAME = "Tacosaurus Computing Center"
REGISTRY_URI = "taco"

# Should registries by default be private, with no option for public?
PRIVATE_ONLY = False

# Should the default for a new registry be private or public?
DEFAULT_PRIVATE = False

# Database
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

########################################################################
# Visualizations
########################################################################

# After how many single containers should we switch to showing collections
# only? >= 1000
VISUALIZATION_TREEMAP_COLLECTION_SWITCH=1000


########################################################################
# Logging
########################################################################


# Logging

# Do you want to save complete response metadata per each pull?
# If you disable, we still keep track of collection pull counts, but not specific versions
LOGGING_SAVE_RESPONSES=True

# Plugins
# Add the name of a plugin under shub.plugins here to enable it

# Available Plugins:
# - ldap_auth: Allows sregistry to authenitcate against an LDAP directory
PLUGINS_ENABLED = [
#    'ldap_auth'
]
