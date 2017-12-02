AUTHENTICATION_BACKENDS = ('shub.plugins.globus_auth.backend.GlobusOAuth2',)

# Show Globus log messages
import logging

logger = logging.getLogger('globus_sdk')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
