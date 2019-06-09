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

### Secrets

Next, set the following variables in `shub/settings/secrets.py`, 
that you can create from `dummy_secrets.py` in the shub/settings folder.
The first two speak for themselves, your project name and path to your
Google Application Credentials.

#### Project Identifiers

```python
# =============================================================================
# Google Cloud Build + Storage
# Configure a custom builder and storage endpoint
# =============================================================================

# google-storage, s3, google-drive, dropbox
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
SREGISTRY_GOOGLE_PROJECT=myproject-ftw

```

You can create custom [Google Application Credentials](https://cloud.google.com/docs/authentication/getting-started) for your server in the browser, and it will be enough to make the service account
a project owner. If you are on a Google Cloud instance you can scp (with gcloud) using the command line as follows:

```bash
$ gcloud compute scp [credentials].json $USER@[INSTANCE]:/tmp --project [PROJECT]
```

Keep in mind that the path to the Google credentials file must be
within the container (/code is the root folder that is bound to the filesystem).

#### Build Caching

```python
SREGISTRY_GOOGLE_BUILD_CACHE="true"
```

If you set this variable (to anything), it means that after build, you will not
delete intermediate dependencies in cloudbuild bucket (keep them as cache for rebuild if needed).
This defaults to being unset, meaning that files are cleaned up. If you define this as anything, 
the build files will be cached.

#### Singularity Version

By default, we use the default version that is set by the [Google Build](https://singularityhub.github.io/sregistry-cli/client-google-build#environment) client that belongs to Singularity Registry Client.
However, as this value is subject to be updated, we recommend that you set it in your
secrets and can then decide when you want to update.

```python
SREGISTRY_GOOGLE_BUILD_SINGULARITY_VERSION="v3.2.1-slim"
```

The version must coincide with a container tag hosted under [singularityware/singularity](https://hub.docker.com/r/singularityware/singularity/).

#### Storage Bucket Name

By default, the bucket name will be called `sregistry-gcloud-build-[hostname]`, and since
your host is a docker container, that will resolve to a random set of numbers and 
letters. Here is an example of how to set a custom name:

```python
SREGISTRY_GOOGLE_STORAGE_BUCKET="taco-singularity-registry"
```

Additionally, a temporary bucket is created with the same name ending in _cloudbuild. This bucket is for build time dependencies, and is cleaned up after the fact. If you are having trouble getting a bucket it is likely because the name is taken, 
and we recommend creating both `[name]` and `[name]_cloudbuild` in the console and then setting the name here.

#### Private Containers

By default, images that you upload will be made public, meaning that a user that stumbles on the URL (or has permission to read your bucket otherwise) will be able to see and download them. If you want to make images globally private you should export this variable as some derivative of yes/true. If no variable is found, images are made public by default.

```python
SREGISTRY_GOOGLE_STORAGE_PRIVATE=True 
```

These variables are written in detail in the dummy_secrets.py file. 
If you need more information, you can read [the Google Cloud Build page](https://singularityhub.github.io/sregistry-cli/client-google-build).

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


### Singularity Registry Client

If you haven't yet, you will need the [sregistry client](https://singularityhub.github.io/sregistry-cli/) in order to push recipes to build with Google Cloud Build. The minimum version that supports this
is `0.2.19`. An easy way to install is any of the following:

```bash
$ pip install sregistry[google-build]
$ pip install sregistry[google-build-basic] # without local sqlite database
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
