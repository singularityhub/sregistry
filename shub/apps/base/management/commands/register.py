"""

Copyright (C) 2017-2021 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.conf import settings
from shub.logger import bot
from shub.settings import ADMINS
from random import choice
from datetime import datetime
import os


class Command(BaseCommand):
    """produce a markdown (.md) file with yml header to submit with PR to
    https://www.github.com/singularityhub/containers to officially
    registry your registry
    """

    help = "produce registration markdown file"

    def handle(self, *args, **options):

        template = "tools/template-registry.md"
        outfile = os.path.basename(template).replace(
            "template-", "%s-" % settings.REGISTRY_URI
        )
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            admin = ADMINS[0][0]
        except:
            admin = "sregistry-robot"
            bot.warning("No admin in settings, will use %s" % admin)

        # Generate a robot number
        number = choice(list(range(1, 15571)))
        context = {
            "REGISTRY_URI": settings.REGISTRY_URI,
            "REGISTRY_NAME": settings.REGISTRY_NAME,
            "DOMAIN_NAME": settings.DOMAIN_NAME,
            "AUTHOR": admin,
            "NUMBER": number,
            "DATETIME_NOW": now,
        }

        content = render_to_string(template, context)

        # Write to file
        with open(outfile, "w") as filey:
            filey.writelines(content)

        bot.newline()
        bot.info("Registry template written to %s!" % outfile)
        bot.newline()
        bot.info(
            "Your robot is at https://vsoch.github.io/robots/assets/img/robots/robot%s.png"
            % number
        )
        bot.info("1. Fork and clone https://www.github.com/singularityhub/containers")
        bot.info("2. Add %s to the registries folder" % outfile)
        bot.info(
            "3. Download your robot (or add custom institution image) under assets/img/[custom/robots]"
        )
        bot.info("4. Submit a PR to validate your registry.")
