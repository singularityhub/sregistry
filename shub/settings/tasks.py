'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from .config import PLUGINS_ENABLED
from kombu import Exchange, Queue
import os

# CELERY SETTINGS
REDIS_DB = 0  
REDIS_HOST = os.environ.get('REDIS_PORT_6379_TCP_ADDR', 'redis')

# CELERY SETTINGS
CELERY_TIMEZONE = 'UTC'
BROKER_TRANSPORT = 'redis'
CELERY_BROKER_TRANSPORT = BROKER_URL = 'redis://%s:6379/0' % REDIS_HOST
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://%s:6379/0' % REDIS_HOST
#CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_DEFAULT_QUEUE = 'default'
CELERY_QUEUES = (
    Queue('default', Exchange('default'), routing_key='default'),
)

# If google_build in use, we are required to include GitHub
if "google_build" in PLUGINS_ENABLED:
    CELERY_IMPORTS = ('shub.apps.api.tasks', 'shub.plugins.google_build.tasks')
else:
    CELERY_IMPORTS = ('shub.apps.api.tasks',)
