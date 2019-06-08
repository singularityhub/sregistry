'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from .config import PLUGINS_ENABLED
from kombu import Exchange, Queue
import os

REDIS_PORT = 6379
REDIS_DB = 0
REDIS_HOST = 'redis'
RABBIT_HOSTNAME = 'rabbit'

BROKER_URL = os.environ.get('BROKER_URL', 'amqp://admin:mypass@rabbit:5672//')
TRANSPORT_URL = BROKER_URL
CELERY_TRANSPORT_URL = BROKER_URL
CELERY_BROKER_URL = BROKER_URL
if not BROKER_URL:
    BROKER_URL = 'amqp://{user}:{password}@{hostname}/{vhost}/'.format(
        user=os.environ.get('RABBIT_ENV_USER', 'admin'),
        password=os.environ.get('RABBIT_ENV_RABBITMQ_PASS', 'mypass'),
        hostname=RABBIT_HOSTNAME,
        vhost=os.environ.get('RABBIT_ENV_VHOST', ''))

print(BROKER_URL)

# We don't want to have dead connections stored on rabbitmq, so we have to negotiate using heartbeats
BROKER_HEARTBEAT = '?heartbeat=60'
if not BROKER_URL.endswith(BROKER_HEARTBEAT):
    BROKER_URL += BROKER_HEARTBEAT

BROKER_POOL_LIMIT = 1
BROKER_CONNECTION_TIMEOUT = 10

# Celery configuration

# configure queues, currently we have only one
CELERY_DEFAULT_QUEUE = 'default'
CELERY_QUEUES = (
    Queue('default', Exchange('default'), routing_key='default'),
)

# Sensible settings for celery
CELERY_ALWAYS_EAGER = False
CELERY_ACKS_LATE = True
CELERY_TASK_PUBLISH_RETRY = True
CELERY_DISABLE_RATE_LIMITS = False

# By default we will ignore result
# If you want to see results and try out tasks interactively, change it to False
# Or change this setting on tasks level
CELERY_IGNORE_RESULT = True
CELERY_SEND_TASK_ERROR_EMAILS = False
CELERY_TASK_RESULT_EXPIRES = 600

# Set redis as celery result backend
CELERY_RESULT_BACKEND = 'redis://%s:%d/%d' % (REDIS_HOST, REDIS_PORT, REDIS_DB)
CELERY_REDIS_MAX_CONNECTIONS = 1

# Don't use pickle as serializer, json is much safer
CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ['application/json']

CELERYD_HIJACK_ROOT_LOGGER = False
CELERYD_PREFETCH_MULTIPLIER = 1
CELERYD_MAX_TASKS_PER_CHILD = 1000

# CELERY SETTINGS
#REDIS_DB = 0  
#REDIS_HOST = os.environ.get('REDIS_PORT_6379_TCP_ADDR', 'redis')

#BROKER_URL = 'django://'
#CELERY_BROKER_URL = 'django://'

#CELERY = {
##    'BROKER_URL': os.environ['CELERY_BROKER'],
#    'BROKER_URL': "amqp://guest@rabbit:5672"
##    'CELERY_IMPORTS': ('shub.apps.api.tasks',),
#    'CELERY_TASK_SERIALIZER': 'json',
#    'CELERY_RESULT_SERIALIZER': 'json',
#    'CELERY_ACCEPT_CONTENT': ['json'],
#    'CELERY_DEFAULT_QUEUE': 'default',
#    'CELERY_QUEUES':(
#        Queue('default', Exchange('default'), routing_key='default'),
#     )
#}

# CELERY SETTINGS
#CELERY_BROKER_URL = "redis://redis:6379/0"
#CELERY_RESULT_BACKEND = "redis://%s:6379/0" % REDIS_HOST
#CELERY_ACCEPT_CONTENT = ['application/json']
#CELERY_TASK_SERIALIZER = 'json'
#CELERY_RESULT_SERIALIZER = 'json'
#CELERY_DEFAULT_QUEUE = 'default'
#CELERY_QUEUES = (
#    Queue('default', Exchange('default'), routing_key='default'),
#)

# If google_build in use, we are required to include GitHub
#if "google_build" in PLUGINS_ENABLED:
#    CELERY_IMPORTS = ('shub.apps.api.tasks', 'shub.plugins.google_build.tasks')
#else:
#    CELERY_IMPORTS = ('shub.apps.api.tasks',)
