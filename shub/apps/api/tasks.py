'''

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
