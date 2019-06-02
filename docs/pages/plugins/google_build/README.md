---
layout: default
title: "Plugin: Custom Builder and Storage"
pdf: true
permalink: /plugin-google-build
toc: true
---

# Plugin: Custom Storage

The Singularity Registry client allows for [a large set](https://singularityhub.github.io/sregistry-cli/clients) of options for external storage endpoints. Specifically, this plugin uses storage and build provided by Google, meaning:

 - [Google Build](https://singularityhub.github.io/sregistry-cli/client-google-build)
 - [Google Storage](https://singularityhub.github.io/sregistry-cli/client-google-storage)

Other cloud vendors have been included with sregistry client (AWS, S3, Minio) and equivalent
build and storage pairs can be added here. If you would like to discuss adding a builder
and storage pair, please [open an issue](https://www.github.com/singularityhub/sregistry).

Don't forget to go back to the [install docs](https://singularityhub.github.io/sregistry/install-server#storage) where you left off.

## Quick Start

This quick start will walk through setting up custom storage using 
[Google Cloud Build](https://singularityhub.github.io/sregistry-cli/client-google-build)
and [Google Storage](https://singularityhub.github.io/sregistry-cli/client-google-storage) as
an endpoint.

### Configure sregistry

By default, google build is disabled. To configure sregistry to 
use Google Cloud build and Storage, in settings/config.py you can enable the plugin by 
uncommenting it from the list here:

```bash
PLUGINS_ENABLED = [
#    'ldap_auth',
#    'saml_auth',
#    'globus',
     'google_build'
]
```

Next, set the following variables in `shub/settings/secrets.py`, 
that you can create from `dummy_secrets.py` in the shub/settings folder:

```python
# =============================================================================
# Google Cloud Build + Storage
# Configure a custom builder and storage endpoint
# =============================================================================

# google-storage, s3, google-drive, dropbox
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
SREGISTRY_GOOGLE_PROJECT=myproject-ftw
...
```

Optional and required variables are written in detail in the dummy_secrets.py file.
If you need more information, you can read 
[the Google Cloud Build page](https://singularityhub.github.io/sregistry-cli/client-google-build).

If you don't want to write these variables into your secrets.py file, you
can also have them available in the environment. In this case, you should put
them into a dictionary called `SREGISTRY_CLIENT_ENVARS` that will be parsed
when the application starts.

```python
SREGISTRY_CLIENT_ENVARS = {
    "SREGISTRY_GOOGLE_PROJECT": "myproject-ftw",
    "GOOGLE_APPLICATION_CREDENTIALS":"/code/credentials.json"}
```

Keep in mind that the path to the Google credentials file must be
within the container (/code is the root folder that is bound to the filesystem).
If you are missing some variable, there will be an error message
on interaction with the Google Cloud Build API since you won't be able to 
authenticate.

*being written*

<div>
    <a href="/sregistry/plugins"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry/plugin-ldap"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
