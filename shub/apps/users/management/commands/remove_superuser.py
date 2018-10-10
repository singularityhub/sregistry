'''

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

'''

from django.core.management.base import (
    BaseCommand,
    CommandError
)

from shub.apps.users.models import User
from shub.logger import bot
import re

class Command(BaseCommand):
    '''remove superuser will remove admin privs for a singularity 
    registry. The super user is an admin that can build, delete,
    and manage images
    '''
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--username', dest='username', default=None, type=str)

    help = "Removes superuser priviledges for the registry."
    def handle(self,*args, **options):
        if options['username'] is None:
            raise CommandError("Please provide a username with --username")

        bot.debug("Username: %s" %options['username']) 

        try:
            user = User.objects.get(username=options['username'])
        except User.DoesNotExist:
            raise CommandError("This username does not exist.")

        if user.is_superuser is False:
            raise CommandError("This user already is not a superuser.")        
        else:
            user.is_superuser = False
            bot.debug("%s is no longer a superuser." %(user.username))
            user.save()
