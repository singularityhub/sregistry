'''

Copyright (C) 2017-2019 Vanessa Sochat.

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

from django.core.management.base import BaseCommand
from django.template.loader import render_to_string 
from django.conf import settings
from shub.logger import bot
from random import choice
from datetime import datetime
import os
import re


class Command(BaseCommand):
    '''produce a markdown (.md) file with yml header to submit with PR to
    https://www.github.com/singularityhub/containers to officially
    registry your registry
    '''
    help = "produce registration markdown file"

    def handle(self,*args, **options):

        template = 'tools/template-registry.md'
        outfile = os.path.basename(template).replace('template-', "%s-" % settings.REGISTRY_URI)
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            admin = ADMINS[0][0]
        except:
            admin = "sregistry-robot"
            bot.warning('No admin in settings, will use %s' %admin)
            pass

        # Generate a robot number
        number = choice(list(range(1,15571)))
        context = {"REGISTRY_URI": settings.REGISTRY_URI,
                   "REGISTRY_NAME": settings.REGISTRY_NAME,
                   "DOMAIN_NAME": settings.DOMAIN_NAME,
                   "AUTHOR": admin,
                   "NUMBER": number,
                   "DATETIME_NOW": now}

        content = render_to_string(template, context)

        # Write to file
        with open(outfile,'w') as filey:
            filey.writelines(content)

        bot.newline()
        bot.info("Registry template written to %s!" %outfile)
        bot.newline()
        bot.info("Your robot is at https://vsoch.github.io/robots/assets/img/robots/robot%s.png" %number)
        bot.info("1. Fork and clone https://www.github.com/singularityhub/containers")
        bot.info("2. Add %s to the registries folder" %outfile)
        bot.info("3. Download your robot (or add custom institution image) under assets/img/[custom/robots]")
        bot.info("4. Submit a PR to validate your registry.")
