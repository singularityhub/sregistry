"""

Copyright (C) 2017-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.core.management.base import BaseCommand
from shub.apps.main.models import Container


class Command(BaseCommand):
    """scheduled to run nightly to clean up dummy containers (control+c)."""

    help = "clean up dummy containers"

    def handle(self, *args, **options):
        Container.objects.filter(tag__startswith="DUMMY-").delete()
