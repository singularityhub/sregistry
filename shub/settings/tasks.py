'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from kombu import Exchange, Queue
import os

# CELERY SETTINGS
REDIS_PORT = 6379  
REDIS_DB = 0  
REDIS_HOST = os.environ.get('REDIS_PORT_6379_TCP_ADDR', 'redis')

# CELERY SETTINGS
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
BROKER_URL = 'redis://redis:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_DEFAULT_QUEUE = 'default'
CELERY_QUEUES = (
    Queue('default', Exchange('default'), routing_key='default'),
)

CELERY_IMPORTS = ('shub.apps.api.tasks',)

CELERY_RESULT_BACKEND = 'redis://%s:%d/%d' %(REDIS_HOST,REDIS_PORT, REDIS_DB)

#BROKER_URL = os.environ.get('BROKER_URL',None)
if BROKER_URL == None:
    BROKER_URL = CELERY_RESULT_BACKEND
