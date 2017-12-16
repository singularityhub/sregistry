'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017 Vanessa Sochat.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

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
