AUTHENTICATION_BACKENDS = ('django_auth_ldap.backend.LDAPBackend',)

# Show LDAP log messages
import logging

logger = logging.getLogger('django_auth_ldap')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

