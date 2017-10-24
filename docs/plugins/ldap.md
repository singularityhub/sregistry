# ldap-auth - Authentication against LDAP directories

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
Hub)](https://hub.docker.com/r/mwaeckerlin/openldap/) is a useful container configured 
with SSL and LDAP.

## Quick Start
This quick start is intended to demonstrate basic functionality of the LDAP server, and you should
review the links referenced about for more detail. After you've completed basic setup in

### What is LDAP?


#### Create the server
As instructed in [https://github.com/mwaeckerlin/openldap](https://github.com/mwaeckerlin/openldap) let's bring 
up a dummy LDAP server:

```
docker run -it --rm --name openldap \
           -p 389:389 \
           -e DEBUG_LEVEL=1 \
           -e DOMAIN=my-company.com \
           -e ORGANIZATION="Tacosaurus Computing Center" \
           -e PASSWORD=avocados \
           mwaeckerlin/openldap
```

**DAVE** can you write a little bit about what this is, what the output means on the screen, and how to map
it to the secrets.py.example? I'd want to be able to know nothing about LDAP, and get this running to test it out.
I gave it my best but once all the output came to the screen I couldn't figure out what to do next.

[..back](../README.md)
