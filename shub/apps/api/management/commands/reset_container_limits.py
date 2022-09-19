"""

Copyright (C) 2017-2022 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.core.management.base import BaseCommand

from shub.apps.main.models import Collection, Container


def reset_limits():
    containers = Container.objects.all()
    containers.update(get_count=0)
    collections = Collection.objects.all()
    collections.update(get_count=0)


class Command(BaseCommand):
    """scheduled to run once a week on Monday, reset get_count to 0."""

    help = "Reset container get counts to 0"

    def handle(self, *args, **options):
        reset_limits()
