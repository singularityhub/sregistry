---
title: "saml-auth - Shibboleth Authentication"
pdf: true
toc: false
permalink: docs/plugins/saml
---

# SAML Authentication

The `saml_auth` plugin allows users to authentication with your [SAML provider](https://en.wikipedia.org/wiki/Security_Assertion_Markup_Language) of choice.

To enable SAML authentication you must:

  * Add `saml_auth` to the `PLUGINS_ENABLED` list in `shub/settings/config.py`
  * Add some configuration details to `shub/settings/config.py`
  * Configure the details of your SAML provider in in `shub/settings/secrets.py` per instructions provided [here](http://python-social-auth.readthedocs.io/en/latest/backends/saml.html).
  * Build the docker image with the build argument ENABLE_SAML set to true:
    ```bash
    $ docker build --build-arg ENABLE_SAML=true -t ghcr.io/singularityhub/sregistry .
    ```


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

so they appear like:


```bash
AUTH_SAML_IDP = "stanford"
AUTH_SAML_INSTITUTION = "Stanford University"
```

#### Setting up SAML Auth

In `secrets.py` you will need to define the variables specified [here](http://python-social-auth.readthedocs.io/en/latest/backends/saml.html), and that includes generating your certificate, which looks something like:

```bash
openssl req -new -x509 -days 3652 -nodes -out saml.crt -keyout saml.key
cat saml.key
mv saml.crt /etc/ssl/certs
mv saml.key /etc/ssl/private
```

and then generate the `metadata.xml` by going to `http://localhost/saml_auth/saml.xml`. Usually institutions have different portals for submitting metadata / getting information about SAML, for Stanford the information is via the [SAML SP Service Provider Database](https://spdb.stanford.edu/).
