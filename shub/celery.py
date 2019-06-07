'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

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
