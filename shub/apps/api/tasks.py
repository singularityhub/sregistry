'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from celery import shared_task, task
from django.conf import settings
import os

@shared_task
def mul(x, y):
    print('RUNNING')
    return x * y

@task
def multask(x, y):
    print('RUNNING')
    return x * y

@shared_task
def expire_share(sid):
    from shub.apps.main.models import Share
    try:
        share = Share.objects.get(id=sid)
        share.delete()
    except Share.DoesNotExist:
        bot.warning("Share %s expired." %sid)
