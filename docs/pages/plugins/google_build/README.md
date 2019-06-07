---
layout: default
title: "Plugin: Custom Builder and Storage"
pdf: true
permalink: /plugin-google-build
toc: true
---

# Plugin: Google Cloud Build and Storage

The Singularity Registry client allows for [a large set](https://singularityhub.github.io/sregistry-cli/clients) of options for external storage endpoints. Specifically, this plugin uses storage and build provided by Google, meaning:

 - [Google Build](https://singularityhub.github.io/sregistry-cli/client-google-build)
 - [Google Storage](https://singularityhub.github.io/sregistry-cli/client-google-storage)

Other cloud vendors have been included with sregistry client (AWS, S3, Minio) and equivalent
build and storage pairs can be added here. If you would like to discuss adding a builder
and storage pair, please [open an issue](https://www.github.com/singularityhub/sregistry).

Don't forget to go back to the [install docs](https://singularityhub.github.io/sregistry/install-settings) where you left off.

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

You can create custom [Google Application Credentials](https://cloud.google.com/docs/authentication/getting-started) for your server in the browser, and it will be enough to make the service account
a project owner. If you are on a Google Cloud instance you can scp (with gcloud) using the command line as follows:

```bash
$ gcloud compute scp [credentials].json $USER@[INSTANCE]:/tmp --project [PROJECT]
```

Optional and required variables are written in detail in the dummy_secrets.py file. 
If you need more information, you can read [the Google Cloud Build page](https://singularityhub.github.io/sregistry-cli/client-google-build).

Keep in mind that the path to the Google credentials file must be
within the container (/code is the root folder that is bound to the filesystem).
If you are missing some variable, there will be an error message
on interaction with the Google Cloud Build API since you won't be able to 
authenticate. Once your settings are ready to go, you will want to continue
with the [install docs](https://singularityhub.github.io/sregistry/install-server#storage) where you left off,
and you can continue here after you've done:

```
$ docker-compose up -d
```

and confirmed the registry running at localhost, and also have logged in
(so you have an account with permission to push containers and recipes.)


### Sregistry Client

If you haven't yet, you will need the [sregistry client](https://singularityhub.github.io/sregistry-cli/) in order to push recipes to build with Google Cloud Build. The minimum version that supports this
is `0.2.19`. An easy way to install is any of the following:

```bash
$ pip install sregistry
$ pip install sregistry[basic] # without local sqlite database
```

Next, export the client to be your registry.

```
$ export SREGISTRY_CLIENT=registry
```

If you are reading here from the installation docs, you likely haven't
brought up your registry and should [return there](https://singularityhub.github.io/sregistry/install-settings) where you left off.

### Push a Recipe

When the server is started and the client is ready, it's time to push a recipe
to build! By default, you will need to specify the name of the collection and
container, and to include the fact that you want to use Google Cloud Build:

```bash
$ sregistry build --name google_build://collection/container:tag Singularity
```

Alternatively, if you only aim to use one builder and want to set it as default,
you can export this once for your session, or more permanently in your bash
profile.

```
export SREGISTRY_BUILD_TYPE=google_build
```

Notice that the command simply requires a name for your collection (it doesn't
need to exist, but you need push access and to have [exported your token](https://singularityhub.github.io/sregistry/credentials) to your local machine. 

<div>
    <a href="/sregistry/plugins"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry/plugin-ldap"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
