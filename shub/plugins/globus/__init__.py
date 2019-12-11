# AUTHENTICATION_BACKENDS = ('shub.plugins.globus.backend.GlobusOAuth2',)

# Show Globus log messages
import logging

logger = logging.getLogger("globus_sdk")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
