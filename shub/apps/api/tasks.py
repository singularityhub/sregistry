'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017 Vanessa Sochat.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from celery import shared_task, Celery
from django.conf import settings
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shub.settings')
app = Celery('shub')
app.config_from_object('django.conf:settings','shub.settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@shared_task
def expire_share(sid):
    from shub.apps.main.models import Share
    try:
        share = Share.objects.get(id=sid)
        share.delete()
    except Share.DoesNotExist:
        bot.warning("Share %s expired." %sid)
