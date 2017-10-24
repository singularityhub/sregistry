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
with unencrypted, StartTLS, and SSL access to an OpenLDAP directory.

## Quick Start
This quick start is intended to demonstrate basic functionality of the LDAP server, and you should
review the links referenced above for more detail. After you've completed basic setup in

### What is LDAP?

LDAP (Lightweight Directory Access Protocol) is a common protocol used by
organizations to hold user information and perform authentication. An LDAP
directory hold records for each user, and groups which users may belong to.

LDAP directories are implemented by many different directory servers. The most
commonly encountered are OpenLDAP on Linux, and Microsoft Active Directory on Windows platforms.

To test sregistry LDAP authentication we can use a dockerized OpenLDAP server.


#### Create the server
As instructed in [https://github.com/mwaeckerlin/openldap](https://github.com/mwaeckerlin/openldap) let's bring 
up a dummy LDAP server:

```
docker run -it --rm --name openldap \
           -p 389:389 \
           -e DEBUG_LEVEL=1 \
           -e DOMAIN=my-company.com \
           -e ORGANIZATION="Tacosaurus" \
           -e PASSWORD=avocados \
           mwaeckerlin/openldap
```

With this command we are:

  - Allowing access on port 389 (unecrypted LDAP / StartTLS encrypted)
  - Creating a directory that will have a `basedn: dc=my-company,dc=com`. The
    basedn is the root of the LDAP directory tree. It is usally created by
    breaking your domain name into domain components (dc).
  - Creating an admin account, which will have the dn (distinguished name)
    `cn=admin,dc=my-company,dc=com` and password `avacados`.

If all goes well, you will see output that ends in:

```
59ef5b78 backend_startup_one: starting "dc=my-company,dc=com"
59ef5b78 hdb_db_open: database "dc=my-company,dc=com": dbenv_open(/var/lib/ldap).
59ef5b78 slapd starting
```

Press `<ctrl+c>` to stop the container. We'll restart an openldap server in the background:

```
docker run -d --name openldap \
           -p 389:389 \
           -e DOMAIN=my-company.com \
           -e ORGANIZATION="Tacosaurus" \
           -e PASSWORD=avocados \
           mwaeckerlin/openldap
           
docker ps

CONTAINER ID        IMAGE                  COMMAND                  CREATED             STATUS              PORTS                           NAMES
398b6297d6ff        mwaeckerlin/openldap   "/bin/sh -c /start.sh"   3 minutes ago       Up 3 minutes        0.0.0.0:389->389/tcp, 636/tcp   openldap
```

#### Add a user and group to the directory

We now need to add some test users and groups to our directory. Create a file
called 'example.ldif' with the following content:

```ldif
##
## Basic LDIF for LDAP simulation setup
## D. C. Trudgian Nov 2014
##

# ----------------------------------------------------------------------------
# STRUCTURE
# ----------------------------------------------------------------------------

dn: ou=users,dc=my-company,dc=com
ou: users
objectClass: top
objectClass: organizationalUnit

dn: ou=groups,dc=my-company,dc=com
ou: Group
objectClass: top
objectClass: organizationalUnit

# ----------------------------------------------------------------------------
# Test Groups
# ----------------------------------------------------------------------------

dn: cn=test,ou=groups,dc=my-company,dc=com
cn: test
description: Test User Group
gidNumber: 1000
objectClass: posixGroup
memberUid: testuser
memberUid: testadmin

dn: cn=admin,ou=groups,dc=my-company,dc=com
cn: admin
description: Test Admin Users
gidNumber: 1002
objectClass: posixGroup
memberUid: testadmin

# ----------------------------------------------------------------------------
# Test Users
# ----------------------------------------------------------------------------

dn: uid=testuser,ou=users,dc=my-company,dc=com
displayName: Test User
cn: Test User
title: Tester
objectClass: inetOrgPerson
objectClass: posixAccount
objectClass: shadowAccount
loginShell: /bin/bash
uidNumber: 1000
gecos: Test User, Test Lab, Test Dept
sn: User
homeDirectory: /home2/testuser
mail: testuser@localhost
givenName: Test
employeeNumber: 1000
shadowExpire: 99999
shadowLastChange: 10000
gidNumber: 1000
uid: testuser
userPassword: {SSHA}IZQSiHPR9A/xKUPTKAM82EJoejtb70vD

dn: uid=testadmin,ou=users,dc=my-company,dc=com
displayName: Test Admin
cn: Test Admin
title: Tester
objectClass: inetOrgPerson
objectClass: posixAccount
objectClass: shadowAccount
loginShell: /bin/bash
uidNumber: 1001
gecos: Test Admin, Test Lab, Test Dept
sn: Admin
homeDirectory: /home2/testadmin
mail: testadmin@localhost
postalAddress: NL5.136
givenName: Test
employeeNumber: 1000
shadowExpire: 99999
shadowLastChange: 10000
gidNumber: 1000
uid: testadmin
userPassword: {SSHA}84O5yFQxQwvQc1Dluc5fJrehrucmCFdH
```

This will create a directory with:

  - Two organizational units (ou=users, ou=groups) to hold our users and groups
  - Two groups, *test* and *admin.*
  - A user *testuser* with password *testuser* who belongs to the *test* group.
  - A user *testadmin* with password *testadmin* who belongs to the *test* and
    *admin* groups.

We use the `ldapadd` command to import this ldif file into our directory:

```bash
cat example.ldif  | docker exec -i openldap ldapadd -x -H ldap://localhost -D 'cn=admin,dc=my-company,dc=com'
-w 'avacados' -v
```

Here `-x` uses simple authentication, `-H` specifies the LDAP server to connect
to, `-D` specifies we want to bind as our admin account and `-w` provides the
password for that account (`-W` would prompt instead).

If all goes well we can check the content of the directory with:

```
docker exec openldap ldapsearch -x -b 'dc=my-company,dc=com'
```

#### Configure sregistry


To configure sregistry to authenticate against our LDAP directory we need to set
the following options in `shub/settings/secrets.py`:

```
# The URI to our LDAP server (may be ldap_auth:// or ldaps://)
AUTH_LDAP_SERVER_URI = "ldap://127.0.0.1"

# Any user account that has valid auth credentials can login
AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=users,dc=my-company,dc=com",
                                   ldap.SCOPE_SUBTREE, "(uid=%(user)s)")

AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=groups,dc=my-company,dc=com",
                                    ldap.SCOPE_SUBTREE, "(objectClass=posixGroup)"
                                    )
AUTH_LDAP_GROUP_TYPE = PosixGroupType()


# Populate the Django user model from the LDAP directory.
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail"
}

# Map LDAP group membership into Django admin flags
AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    # Anyone in this group is a superuser for the app
    "is_superuser": "cn=admin,ou=groups,dc=biohpc,dc=swmed,dc=edu"
}
```

Also ensure 'ldap-auth' is listed in `PLUGINS_ENABLED` inside `shub/settings/config.py`.

Once you have set these options, startup sregistry and you should be able to
login with the username/password pairs *testuser/testuser* and *testadmin/testadmin*.


[..back](../README.md)
