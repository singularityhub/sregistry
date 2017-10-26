# ldap-auth - Authentication against LDAP directories

The `ldap-auth` plugin allows users to login to sregistry using account information stored in an
LDAP directory. This supports logins against [Microsoft Active Directory](https://msdn.microsoft.com/en-us/library/bb742424.aspx), as well open-source
[OpenLDAP](https://www.openldap.org/) etc.

To enable LDAP authentication you must:

  * Uncomment the Dockerfile section to install LDAP dependencies *before* building the image
  * Add `ldap-auth` to the `PLUGINS_ENABLED` list in `shub/settings/config.py`
  * Configure the details of your LDAP directory in `shub/settings/secrets.py`. See
    `shub/settings/dummy_secrets.py` for an example OpenLDAP configuration. A good start is to do the following:

```
cp shub/settings/dummy_secrets.py shub/settings/secrets.py
```
  
Because no two LDAP directories are the same, configuration can be complex and there are no
standard settings. The plugin uses `django-auth-ldap`, which provides more [detailed documentation
at Read the Docs](https://django-auth-ldap.readthedocs.io/en/1.2.x/authentication.html).

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

To test sregistry LDAP authentication we can use a Dockerized OpenLDAP server.


#### Create the server
As instructed in [https://github.com/mwaeckerlin/openldap](https://github.com/mwaeckerlin/openldap) and [(here!)](https://marc.xn--wckerlin-0za.ch/computer/setup-openldap-server-in-docker)  let's bring 
up a dummy LDAP server:

```
docker run -d --restart unless-stopped \
              --name openldap \
              -p 389:389 \
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
    `cn=admin,dc=my-company,dc=com` and password `avocados`.

The `-d` means "detached" so you won't see the output in the terminal. If you need to see output, remove the `-d`. Here is the 
running container:

```
docker ps

CONTAINER ID        IMAGE                  COMMAND                  CREATED             STATUS              PORTS                           NAMES
398b6297d6ff        mwaeckerlin/openldap   "/bin/sh -c /start.sh"   3 minutes ago       Up 3 minutes        0.0.0.0:389->389/tcp, 636/tcp   openldap
```

#### Interact with it
Here is a way to get familiar with the executables inside the image for ldap:

```
docker exec -it openldap bash

root@docker[72b21bd3c290]:/# which ldapadd
/usr/bin/ldapadd

root@docker[72b21bd3c290]:/# which ldapwhoami
/usr/bin/ldapwhoami
```

Note that the long string with cn= through dc= is your username! The password is the one you set for the image.

```
root@docker[4ec2c4f2737a]:/# ldapwhoami -x -D 'cn=admin,dc=my-company,dc=com' -W
Enter LDAP Password:
dn:cn=admin,dc=my-company,dc=com
```

For the password above you would enter the one we set in the environment for the image. In our case this was `avocados`.

#### Add a user and group to the directory

If all has gone well we can check the content of the directory with:

```
$ ldapsearch -x -b 'dc=my-company,dc=com'

# extended LDIF
#
# LDAPv3
# base <dc=my-company,dc=com> with scope subtree
# filter: (objectclass=*)
# requesting: ALL
#

# my-company.com
dn: dc=my-company,dc=com
objectClass: top
objectClass: dcObject
objectClass: organization
o: Tacosaurus
dc: my-company

# admin, my-company.com
dn: cn=admin,dc=my-company,dc=com
objectClass: simpleSecurityObject
objectClass: organizationalRole
cn: admin
description: LDAP administrator

# search result
search: 2
result: 0 Success

# numResponses: 3
# numEntries: 2
```

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

We use the `ldapadd` command to import this ldif file into our directory (note this will prompt for the password):

```bash
cat example.ldif  | ldapadd -x -H ldap://localhost -D 'cn=admin,dc=my-company,dc=com' -W -v
```

The variables mean the following:

  - `-x` uses simple authentication
  - `-H` specifies the LDAP server to connect to
  - `-D` specifies we want to bind as our admin account
  - `-W` prompts for the password for that account

**Important** You need to get the ip-address of your ldap server. Since we aren't using docker-compose,
the containers won't magically see one another. You can do that as follows:

```
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' openldap
172.17.0.2
```
Note that you will need this address in the next step for `AUTH_LDAP_SERVER_URI`.

#### Configure sregistry

To configure sregistry to authenticate against our LDAP directory we need to set
the following options in `shub/settings/secrets.py`:

```
import ldap
from django_auth_ldap.config import LDAPSearch, PosixGroupType

# The URI to our LDAP server (may be ldap_auth:// or ldaps://)
AUTH_LDAP_SERVER_URI = "ldap://172.17.0.2"

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
    "is_superuser": "cn=admin,ou=groups,dc=my-company,dc=com"
}
```

Also ensure 'ldap-auth' is listed in `PLUGINS_ENABLED` inside `shub/settings/config.py`.

It's recommended to have the uwsgi logs open so any issue with ldap is shown clearly. You can do that with:

```
docker-compose logs -f uwsgi
```

For example, if you put in an incorrect credential, you would see the following in the logs:

```
uwsgi_1   | [pid: 56|app: 0|req: 4/4] 172.17.0.1 () {42 vars in 1025 bytes} [Thu Oct 26 07:18:10 2017] GET /ldap_auth/login/?next=http://127.0.0.1/login/ => generated 13475 bytes in 26 msecs (HTTP/1.1 200) 7 headers in 382 bytes (1 switches on core 0)
uwsgi_1   | search_s('ou=users,dc=my-company,dc=com', 2, '(uid=%(user)s)') returned 0 objects: 
uwsgi_1   | Authentication failed for adminuser: failed to map the username to a DN.
```

Once you have set these options, startup sregistry and you should be able to see the ldap option on the login page:

![img/ldap.png](img/ldap.png)

and login with the username/password pairs *testuser/testuser* and *testadmin/testadmin*. As a final note, if you choose this method to deploy an actual ldap server, you might consider adding the container to the docker-compose. If you've done this and need help, or want to contribute what you've learned, please submit a Pull Request to update these docs.


[..back](../README.md)
