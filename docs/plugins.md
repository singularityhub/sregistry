# Plugins

Singularity Registry supports added functionality through plugins. Plugins allow complex features,
such as container scanning, LDAP authentication, to be added without complicating the core code of
sregistry.

Plugins distributed with sregistry are found in the `shub/plugins` directory. 

## Included Plugins

The following plugins are included with sregistry, and can be enabled by adding them to the
`PLUGINS_ENABLED` entry in `shub/settings/config.py`. Plugins may require further configuration in
your registries' local `shub/settings/secrets/py` file.


### ldap-auth - Authentication against LDAP directories

The `ldap-auth` plugin allows users to login to sregistry using account information stored in an
LDAP directory. This supports logins against Microsoft Active Directory, as well open-source
OpenLDAP etc.

To enable LDAP authentication you must:

  * Add `ldap-auth` to the `PLUGINS_ENABLED` list in `shub/settings/config.py`
  * Configure the details of your LDAP directory in `shub/settings/secrets.py`. See
    `shub/settings/secrets.py.example` for an example OpenLDAP configuration.
  
Because no two LDAP directories are the same, configuration can be complex and there are no
standard settings. The plugin uses `django-auth-ldap`, which provides more [detailed documentation
at Read the Docs here](https://django-auth-ldap.readthedocs.io/en/1.2.x/authentication.html).

To test LDAP authentication you may wish to use a docker container that provides an OpenLDAP
directory. `mwaeckerlin/openldap` [(GitHub)](https://github.com/mwaeckerlin/openldap) [(Docker
Hub)](https://hub.docker.com/r/mwaeckerlin/openldap/) is a useful container configured with SSL and


## Writing a Plugin

An sregistry plugin is a Django App, that lives inside `shub/plugins/<plugin-name>`.

The plugin interface is currently under development. At present, each plugin:

 - Must provide a `urls.py` listing any URLs that will be exposed under `/plugin-name`
 - Can provide additional, models, views, templates, static files.
 - Can register an additional `AUTHENTICATION_BACKEND` by specifying `AUTHENTICATION_BACKEND` in
   its `__init.py__`

Plugins are loaded when the plugin name is added to `PLUGINS_ENABLED` in `shub/settings/config.py`.
A plugin mentioned here is added to `INSTALLED_APPS` at runtime, and any `AUTHENTICATION_BACKEND`
listed in the plugin `__init.py__` is merged into the project settings.

More documentation will be added as the plugin interface is developed. For now, see plugins
distrubuted with sregisty under `shub/plugins` for example code.
