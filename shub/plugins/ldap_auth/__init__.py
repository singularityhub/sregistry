# Show LDAP log messages
import logging

AUTHENTICATION_BACKENDS = ("django_auth_ldap.backend.LDAPBackend",)

logger = logging.getLogger("django_auth_ldap")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
