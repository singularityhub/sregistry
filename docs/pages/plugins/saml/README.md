---
layout: default
title: "saml-auth - Shibboleth Authentication"
pdf: true
permalink: /plugin-saml
toc: false
---

The `saml-auth` plugin allows users to authentication with your [SAML provider](https://en.wikipedia.org/wiki/Security_Assertion_Markup_Language) of choice.

To enable SAML authentication you must:

  * Add `saml-auth` to the `PLUGINS_ENABLED` list in `shub/settings/config.py`
  * Add some configuratoin detials to `shub/settings/config.py`
  * Configure the details of your SAML provider in in `shub/settings/secrets.py`. See
    `shub/settings/dummy_secrets.py` for an example configuration. 

If you haven't yet created a secrets.py, a good start is to do the following:

```
cp shub/settings/dummy_secrets.py shub/settings/secrets.py
```
  
## Quick Start
This quick start is intended to demonstrate basic functionality of the SAML authentication. 


#### Edit Config.py

In the file `shub/settings/config.py` you should add the name of your institution (used to render the button)
along with the idp (the unique identifier for your SAML server request). That means uncommenting these lines.

```bash
# AUTH_SAML_IDP = "stanford"
# AUTH_SAML_INSTITUTION = "Stanford University"
```


#### Setting up SAML Auth

In `secrets.py` you will need to define the variables specified [here](http://python-social-auth.readthedocs.io/en/latest/backends/saml.html), and that includes generating your certificate, which looks something like:

```bash
openssl req -new -x509 -days 3652 -nodes -out saml.crt -keyout saml.key
cat saml.key
mv saml.crt /etc/ssl/certs
mv saml.key /etc/ssl/private
```

and then generate the `metadata.xml` by going to `http://localhost/saml.xml`. Usually institutions have different portals for submitting metadata / getting information about SAML, for Stanford the information is via the [SAML SP Service Provider Database](https://spdb.stanford.edu/).


### Pubmed ID Cache
To make the searches more in sync with your particular datastore, it makes sense to cache the ids in your database, and only present articles to uses that are present. Toward this aim, you should run [this script](scripts/generate_pubmed_cache.py) inside your instance to generate the first cache. It's not required, but helpful.


### Google Storage CORS
If you are creating your own bucket, you will need to use gsutil to set up CORS, with an example (for doc.fish domain) provided in [scripts/google_cloud_storage_cors.json](scripts/google_cloud_storage_cors.json). You would run as follows:

```
gsutil cors set scripts/google_cloud_storage_cors.json gs://pmc-stanford
```

<div>
    <a href="/sregistry/plugins/plugin-ldap"><button class="previous-button btn btn-primary"><i class="fa fa-chevron-left"></i> </button></a>
    <a href="/sregistry/plugin-globus"><button class="next-button btn btn-primary"><i class="fa fa-chevron-right"></i> </button></a>
</div><br>
