# This file, dummy_secrets, provides an example of how to configure
# sregistry with your authentication secrets. Copy it to secrets.py and
# configure the settings you need.

# Secret Key
# You must uncomment, and set SECRET_KEY to a secure random value
# e.g. https://djskgen.herokuapp.com/

#SECRET_KEY = 'xxxxxxxxxxxxxxxxxx'


# =============================================================================
# Social Authentication
# Set keys and secrets for social authentication methods that you have
# enabled in config.py.
# See https://singularityhub.github.io/sregistry/install.html for full details
# =============================================================================

# Twitter OAuth2
# Only required if ENABLE_TWITTER_AUTH=TRUE in config.py
#SOCIAL_AUTH_TWITTER_KEY = ''
#SOCIAL_AUTH_TWITTER_SECRET = ''

# -----------------------------------------------------------------------------
# Google OAuth2
# Only required if ENABLE_GOOGLE_AUTH=TRUE in config.py

#GOOGLE_CLIENT_FILE='/code/.grilledcheese.json'

# http://psa.matiasaguirre.net/docs/backends/google.html?highlight=google
#SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'xxxxxxxxxxxxxxxxxx.apps.googleusercontent.com'
#SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'xxxxxxxxxxxxxxxxx'

# The scope is not needed, unless you want to develop something new.
#SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['https://www.googleapis.com/auth/drive']
#SOCIAL_AUTH_GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {
#    'access_type': 'offline',
#    'approval_prompt': 'auto'
#}
# -----------------------------------------------------------------------------
# GitHub OAuth
# Only required if ENABLE_GITHUB_AUTH=TRUE in config.py
#http://psa.matiasaguirre.net/docs/backends/github.html?highlight=github

#SOCIAL_AUTH_GITHUB_KEY = ''
#SOCIAL_AUTH_GITHUB_SECRET = ''

# You shouldn't actually need this if we aren't using repos
# SOCIAL_AUTH_GITHUB_SCOPE = ["repo","user"]

# -----------------------------------------------------------------------------
# GitLab OAuth2

#SOCIAL_AUTH_GITLAB_SCOPE = ['api', 'read_user']
#SOCIAL_AUTH_GITLAB_KEY = ''
#SOCIAL_AUTH_GITLAB_SECRET = ''

# =============================================================================
# Google Cloud Build + Storage
# Configure a custom builder and storage endpoint
# =============================================================================

# GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
# SREGISTRY_GOOGLE_PROJECT="myproject-ftw"

# SREGISTRY_GOOGLE_BUILD_CACHE="true"
# After build, do not delete intermediate dependencies in cloudbuild bucket (keep them as cache for rebuild if needed). 
# Defaults to being unset, meaning that files are cleaned up. If you define this as anything, the build files will be cached.

# SREGISTRY_GOOGLE_BUILD_SINGULARITY_VERSION="v3.2.1-slim"
# if you want to specify a version of Singularity. The version must coincide with a container tag hosted under singularityware/singularity. The version will default to 3.2.0-slim If you want to use a different version, update this variable.

# SREGISTRY_GOOGLE_STORAGE_BUCKET="taco-singularity-registry"
# is the name for the bucket you want to create. The example here is using the unique identifier appended with “sregistry-" 
# If you don't define it, it will default to a string that includes the hostname.
# Additionally, a temporary bucket is created with the same name ending in _cloudbuild. This bucket is for build time dependencies, and is cleaned up after the fact. If you are having trouble getting a bucket it is likely because the name is taken, 
# and we recommend creating both <name> and <name>_cloudbuild in the console and then setting the name here.

# SREGISTRY_GOOGLE_STORAGE_PRIVATE=True 
# by default, images that you upload will be made public, meaning that a user that stumbles on the URL (or has permission to read your bucket otherwise) will be able to see and download them. If you want to make images globally private you should export this variable as some derivative of yes/true. If no variable is found, images are made public by default.

# GOOGLE_PROJECT_NUMBER=1234455555555
# required to receive notifications for cloud build.

# -----------------------------------------------------------------------------
# Bitbucket OAuth2

# SOCIAL_AUTH_BITBUCKET_OAUTH2_KEY = '<your-consumer-key>'
# SOCIAL_AUTH_BITBUCKET_OAUTH2_SECRET = '<your-consumer-secret>'
# SOCIAL_AUTH_BITBUCKET_OAUTH2_VERIFIED_EMAILS_ONLY = True

# =============================================================================
# Plugin Authentication
# Set options for authentication plugins that you have enabled in config.py
# =============================================================================

# LDAP Authentication (ldap-auth)
# Only required if 'ldap-auth' is added to PLUGINS_ENABLED in config.py

# This example assumes you are using an OpenLDAP directory
# If using an alternative directory - e.g. Microsoft AD, 389 you
# will need to modify attribute names/mappings accordingly
# See https://django-auth-ldap.readthedocs.io/en/1.2.x/index.html

# To work with OpenLDAP and posixGroup groups we need to import some things
#import ldap
#from django_auth_ldap.config import LDAPSearch, PosixGroupType

# The URI to our LDAP server (may be ldap:// or ldaps://)
#AUTH_LDAP_SERVER_URI = "ldaps://ldap.example.com

# DN and password needed to bind to LDAP to retrieve user information
# Can leave blank if anonymous binding is sufficient
#AUTH_LDAP_BIND_DN = ""
#AUTH_LDAP_BIND_PASSWORD = ""

# Any user account that has valid auth credentials can login
#AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=users,dc=example,dc=com",
#                                   ldap.SCOPE_SUBTREE, "(uid=%(user)s)")

#AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=groups,dc=example,dc=com",
#                                    ldap.SCOPE_SUBTREE, "(objectClass=posixGroup)"
#                                    )
#AUTH_LDAP_GROUP_TYPE = PosixGroupType()

# Populate the Django user model from the LDAP directory.
#AUTH_LDAP_USER_ATTR_MAP = {
#    "first_name": "givenName",
#    "last_name": "sn",
#    "email": "mail"
#}

# Map LDAP group membership into Django admin flags
#AUTH_LDAP_USER_FLAGS_BY_GROUP = {
#    "is_superuser": "cn=sregistry_admin,ou=groups,dc=example,dc=com"
#}

# AUTH_LDAP_USER_FLAGS_BY_GROUP = {

#    # Anyone in this group can get a token to manage images, not superuser
#    "is_staff": "cn=staff,ou=django,ou=groups,dc=example,dc=com",
#
#    # Anyone in this group is a superuser for the app
#    "is_superuser": "cn=superuser,ou=django,ou=groups,dc=example,dc=com"

# }

# Globus Assocation (globus)
# Only required if 'globus' is added to PLUGINS_ENABLED in config.py

#SOCIAL_AUTH_GLOBUS_KEY="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
#SOCIAL_AUTH_GLOBUS_USERNAME="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@clients.auth.globus.org"
#SOCIAL_AUTH_GLOBUS_SECRET="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
#GLOBUS_ENDPOINT_ID="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


# SAML Authentication (saml)
# Only required if 'saml_auth' is added to PLUGINS_ENABLED in config.py

# AUTH_SAML_IDP = "stanford"
# AUTH_SAML_INSTITUTION = "Stanford University"
