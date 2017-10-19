from importlib import import_module

from .applications import *
from .config import *
from .main import *
from .auth import *
from .api import *
from .tasks import *

# Apply any plugin settings
for plugin in PLUGINS_ENABLED:

    plugin_module = 'shub.plugins.' + plugin
    plugin = import_module(plugin_module)

    # Add the plugin to INSTALLED APPS
    INSTALLED_APPS.append(plugin_module)

    # Add AUTHENTICATION_BACKENDS if defined, for authentication plugins
    if hasattr(plugin, 'AUTHENTICATION_BACKENDS'):
        AUTHENTICATION_BACKENDS = AUTHENTICATION_BACKENDS + plugin.AUTHENTICATION_BACKENDS


