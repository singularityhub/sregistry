'''

Copyright (c) 2017, Vanessa Sochat, All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''

from django.core.management.base import BaseCommand
from django.template.loader import render_to_string 
from shub.settings import (
    REGISTRY_URI, 
    REGISTRY_NAME, 
    DOMAIN_NAME,
    ADMINS
)

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
        outfile = os.path.basename(template).replace('template-', "%s-" %REGISTRY_URI)
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            admin = ADMINS[0][0]
        except:
            admin = "sregistry-robot"
            bot.warning('No admin in settings, will use %s' %admin)
            pass

        # Generate a robot number
        number = choice(list(range(1,15571)))
        context = {"REGISTRY_URI":REGISTRY_URI,
                   "REGISTRY_NAME":REGISTRY_NAME,
                   "DOMAIN_NAME": DOMAIN_NAME,
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
        bot.info("1. Fork and clone https://www.github.com/singularityhub/sregistry")
        bot.info("2. Add %s to the registries folder" %outfile)
        bot.info("3. Download your robot (or add custom institution image) under assets/img/[custom/robots]")
        bot.info("4. Submit a PR to validate your registry.")
