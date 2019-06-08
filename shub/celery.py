'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from __future__ import absolute_import, unicode_literals
import os
from django.conf import settings
from django.apps import apps
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shub.settings')
shubcelery = Celery('shub')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
shubcelery.config_from_object('django.conf:settings', namespace="CELERY")
shubcelery.conf.imports = settings.CELERY_IMPORTS

# This is important! autodiscover_tasks() is supposed to work without
# providing names, but it doesn't.
shubcelery.autodiscover_tasks(lambda: [a.name for a in apps.get_app_configs()])
