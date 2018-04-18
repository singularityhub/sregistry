---
layout: default
title: Plugins
pdf: true
permalink: /plugins
toc: false
---

# Plugins

Singularity Registry Server supports added functionality through plugins. Plugins allow complex features,
such as container scanning, LDAP authentication, to be added without complicating the core code of
sregistry.

Plugins distributed with `sregistry` are found in the `shub/plugins` directory. 

## Included Plugins

The following plugins are included with sregistry, and can be enabled by adding them to the
`PLUGINS_ENABLED` entry in `shub/settings/config.py`. Plugins may require further configuration in
your registries' local `shub/settings/secrets.py` file.

 - [LDAP-AUTH](/sregistry/plugin-ldap): authentication against LDAP directories
 - [GLOBUS-AUTH](/sregistry/plugin-globus): authentication using Globus


## Writing a Plugin

An sregistry plugin is a Django App, that lives inside `shub/plugins/<plugin-name>`.

The plugin interface is currently under development. At present, each plugin:

 - Must provide a `urls.py` listing any URLs that will be exposed under `/plugin-name`
 - Can provide additional, models, views, templates, static files.
 - Can register an additional `AUTHENTICATION_BACKEND` by specifying `AUTHENTICATION_BACKEND` in
   its `__init.py__`
 - Must provide a documentation file and link in this README.

Plugins are loaded when the plugin name is added to `PLUGINS_ENABLED` in `shub/settings/config.py`.
A plugin mentioned here is added to `INSTALLED_APPS` at runtime, and any `AUTHENTICATION_BACKEND`
listed in the plugin `__init.py__` is merged into the project settings.

More documentation will be added as the plugin interface is developed. For now, see plugins
distrubuted with sregisty under `shub/plugins` for example code.

## Writing Documentation
Documentation for your plugin is just as important as the plugin itself! You should create a subfolder under
`docs/pages/plugins/<your-plugin>` with an appropriate README.md that is linked to in this file.
Use the others as examples to guide you.


<div>
    <a href="/sregistry/credentials"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry/interface"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
