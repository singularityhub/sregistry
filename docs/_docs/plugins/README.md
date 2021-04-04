---
title: Plugins
pdf: true
toc: false
permalink: docs/plugins/
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

 - [LDAP-Auth](ldap): authentication against LDAP directories
 - [PAM-Auth](pam): authentication using PAM (unix host users)
 - [Globus](globus): connect and transfer using Globus
 - [SAML](saml): Authentication with SAML
 - [Google Build](google-build) provides build and storage on Google Cloud.
 - [Keystore](pgp) provides a standard keystore for signing containers
 - [Remote Build](remote-build) provides a library endpoint to remotely build container

The Dockerfile has some build arguments to build the Docker image according to the plugins software requirements. These variables are set to false by default:

```bash
ARG ENABLE_LDAP=false
ARG ENABLE_PAM=false
ARG ENABLE_GOOGLEBUILD=false
ARG ENABLE_GLOBUS=false
ARG ENABLE_SAML=false
ARG ENABLE_REMOTEBUILD=false
```

Therefore, if you want to install the requirements of all current supported plugins, you can build the image as follows: 
```bash
docker build --build-arg ENABLE_LDAP=true --build-arg ENABLE_PAM=true  --build-arg ENABLE_GOOGLEBUILD=true --build-arg ENABLE_GLOBUS=true --build-arg ENABLE_SAML=true -t quay.io/vanessa/sregistry .
```


## Writing a Plugin

An sregistry plugin is a Django App, that lives inside `shub/plugins/<plugin-name>`.
Each plugin:

 - Must provide a `urls.py` listing any URLs that will be exposed under `/plugin-name`
 - Can provide additional, models, views, templates, static files.
 - Can register an additional `AUTHENTICATION_BACKEND` by specifying `AUTHENTICATION_BACKEND` in
   its `__init.py__`
 - Can register additional context processors by defining a tuple of complete paths to the relevant processors by specifying `CONTEXT_PROCESSORS` in its `__init.py__`
 - Must provide a documentation file and link in this README.

Plugins are loaded when the plugin name is added to `PLUGINS_ENABLED` in `shub/settings/config.py`.
A plugin mentioned here is added to `INSTALLED_APPS` at runtime, and any `AUTHENTICATION_BACKEND`
and `CONTEXT_PROCESSORS` listed in the plugin `__init.py__` is merged into the project settings.

More documentation will be added as the plugin interface is developed. For now, see plugins
distrubuted with sregisty under `shub/plugins` for example code.

Besides, if your plugin has any specific software requirements that are not currently available in the Docker image and **those requirements are compatible with the current software**, you can set a new build argument `ENABLE_{PLUGIN_NAME}` and add the corresponding installation commands in the `PLUGINS` section of the Dockerfile with the following format:
```bash
RUN if $ENABLE_{PLUGIN_NAME}; then {INSTALLATION_COMMAND}; fi;
```
## Writing Documentation
Documentation for your plugin is just as important as the plugin itself! You should create a subfolder under
`docs/_docs/plugins/<your-plugin>` with an appropriate README.md that is linked to in this file.
Use the others as examples to guide you.

