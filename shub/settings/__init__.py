from importlib import import_module

from .api import *
from .applications import *
from .auth import *
from .config import *
from .logging import *
from .main import *
from .tasks import *

# If PAM_AUTH in plugins enbled, add django_pam
if "pam_auth" in PLUGINS_ENABLED:
    INSTALLED_APPS += ["django_pam"]

if "remote_build" in PLUGINS_ENABLED:
    INSTALLED_APPS += ["channels"]
# ASGI_APPLICATION should be set to your outermost router
    ASGI_APPLICATION = 'shub.plugins.remote_build.routing.application'

# Channel layer definitions
# http://channels.readthedocs.io/en/latest/topics/channel_layers.html

#    redis_host = os.environ.get('REDIS_HOST', '172.16.0.8')
#
#     CHANNEL_LAYERS = {
#         "default": {
#             # This example app uses the Redis channel layer implementation channels_redis
#             "BACKEND": "channels_redis.core.RedisChannelLayer",
#            "CONFIG": {
#                 "hosts": [(redis_host, 6379)],
#             },
#         },
#    }

# If google_build in use, we are required to include GitHub
if "google_build" in PLUGINS_ENABLED:

    # For task discovery by celery
    SOCIAL_AUTH_GITHUB_SCOPE = [
        "admin:repo_hook",
        "repo:status",
        "user:email",
        "read:org",
        "admin:org_hook",
        "deployment_status",
    ]
    ENABLE_GITHUB_AUTH = True

# Apply any plugin settings
for plugin in PLUGINS_ENABLED:

    plugin_module = "shub.plugins." + plugin
    plugin = import_module(plugin_module)

    # Add the plugin to INSTALLED APPS
    INSTALLED_APPS.append(plugin_module)

    # Add AUTHENTICATION_BACKENDS if defined, for authentication plugins
    if hasattr(plugin, "AUTHENTICATION_BACKENDS"):
        AUTHENTICATION_BACKENDS = (
            AUTHENTICATION_BACKENDS + plugin.AUTHENTICATION_BACKENDS
        )

    # Add custom context processors, if defines for plugin
    if hasattr(plugin, "CONTEXT_PROCESSORS"):
        for context_processor in plugin.CONTEXT_PROCESSORS:
            TEMPLATES[0]["OPTIONS"]["context_processors"].append(context_processor)
