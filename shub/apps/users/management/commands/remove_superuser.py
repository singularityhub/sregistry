"""

Copyright (C) 2017-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.core.management.base import BaseCommand, CommandError

from shub.apps.users.models import User
from shub.logger import bot


class Command(BaseCommand):
    """remove superuser will remove admin privs for a singularity
    registry. The super user is an admin that can build, delete,
    and manage images
    """

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument("--username", dest="username", default=None, type=str)

    help = "Removes superuser priviledges for the registry."

    def handle(self, *args, **options):
        if options["username"] is None:
            raise CommandError("Please provide a username with --username")

        bot.debug("Username: %s" % options["username"])

        try:
            user = User.objects.get(username=options["username"])
        except User.DoesNotExist:
            raise CommandError("This username does not exist.")

        if user.is_superuser is False:
            raise CommandError("This user already is not a superuser.")
        else:
            user.is_superuser = False
            bot.debug("%s is no longer a superuser." % (user.username))
            user.save()
