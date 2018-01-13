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

'''

from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shub.settings')
shubcelery = Celery('shub')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
shubcelery.config_from_object('django.conf:settings')
shubcelery.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

from opbeat.contrib.django.models import (
    client, 
    logger, 
    register_handlers
)

from opbeat.contrib.celery import register_signal

try:
    register_signal(client)

except Exception as e:
    logger.exception('Failed installing celery hook: %s' % e)

if 'opbeat.contrib.django' in settings.INSTALLED_APPS:
    register_handlers()
