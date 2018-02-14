# -*- coding: utf-8 -*-

'''

Copyright (C) 2017-2018 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017-2018 Vanessa Sochat.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

See https://github.com/singularityhub/sregistry/issues/89 for full discussion
    Each set of groups is defined around permissions to create/update/delete 
    objects

Groups:

Superuser

    has all permissions, can do anything, 
    this maps to the Django superuser role. 

Content Admin

    A content admin can generate collections and containers as well as interact 
    with them, and can  additionally grant content user's the permission to be 
    a Collection Admin.

Collection Admin

    A collection admin can generate collections and containers as well as 
    interact with them, but only can control those that he creates.

Content User

    A content user is primarily concerned with pulling or using containers. 
    A content user has an account, and has a token to use the Registry. 
    A token is not required for public images, and a token is required for 
    private images.


Visitor (no permissions)
    The visitor can browse the registry (if the portal is web accessible to 
    everyone) and view public collections. Public collections can be pulled, 
    and that's it.

'''

from __future__ import unicode_literals
from django.contrib.auth.models import ( User, Group, Permission )
from django.db import ( models, migrations )

def save_permissions(name, permissions=None):
    '''save_permissions will create a group based on "name," and optionally add
       (global) permissions to it
       

       Parameters
       ==========
       name: the name of a group to add, should be lowercase with no special
             characters
       permissions: a list of one or more permission labels

    '''

    group, _ = Group.objects.get_or_create(name=name)
    print('\nCreating group %s' %name)
    if permissions is not None:
        perms = Permission.objects.filter(codename__in=permissions)
        found = [x.codename for x in perms]
        group.permissions.set(perms)
        print('\n'.join(found))
    group.save()


def create_groups(apps, schema_editor):
    '''create groups will generate the different permissions groups. The global
       permissions are defined, and object level permissions noted (and created
       with objects.
    '''


    # Visitors: no permissions or group (anon)

    # Content User: can be given pull_container on private

    save_permissions('content-user')


    # Collection Admin

    permissions = [ 'create_token',
                    'create_collection' ]

    save_permissions('collection-admins', permissions)

    # Specific (Object) Permissions
    # change collection privacy (specific)
    # pull container (global public, specific private)
    # push container (specific)
    # delete collection (specific)
    # update collection (specific)
    # create container (specific)
    # delete container (specific)
    # update container (specific)

    # Content admin have global permissions

    permissions += [ 'create_permission', # needs to just be collection admin permission
                     'delete_permission',
                     'change_permission' ]
    
    save_permissions('content-admins', permissions)


    # Specific (Object) Permissions
    # assign Collection Admin Group
    # revoke Collection Admin Group
    # change collection privacy (specific)
    # pull container (specific)
    # push container (specific)
    # delete collection (specific)
    # update collection (specific)
    # create container (specific)
    # delete container (specific)
    # update container (specific)


    # Superusers have global permissions

    permissions += ['change_collection',
                    'pull_collection',
                    'push_collection',
                    'create_collection',
                    'delete_collection',
                    'create_permission',
                    'delete_permission',
                    'change_permission',
                    'create_group',
                    'delete_group',
                    'modify_group' ]

    save_permissions('superusers', permissions)


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_groups),
    ]
