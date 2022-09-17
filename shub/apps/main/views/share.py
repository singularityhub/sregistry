"""

Copyright (C) 2017-2022 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from datetime import datetime

import django_rq
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import reverse
from ratelimit.decorators import ratelimit

from shub.apps.api.tasks import expire_share
from shub.apps.main.utils import calculate_expiration_date
from shub.apps.main.views import get_container
from shub.settings import VIEW_RATE_LIMIT as rl_rate
from shub.settings import VIEW_RATE_LIMIT_BLOCK as rl_block


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
@login_required
def generate_share(request, cid):
    """generate a temporary share link for a container

    Parameters
    ==========
    cid: the container to generate a share link for
    """
    from shub.apps.main.models import Share

    container = get_container(cid)
    edit_permission = container.has_edit_permission(request)

    if edit_permission:
        days = request.POST.get("days", None)
        if days is not None:
            days = int(days)
            try:
                expire_date = calculate_expiration_date(days)
                share, _ = Share.objects.get_or_create(
                    container=container, expire_date=expire_date
                )
                share.save()

                # Generate an expiration task
                django_rq.enqueue(expire_share, sid=share.id, eta=expire_date)

                link = reverse(
                    "download_share",
                    kwargs={"cid": container.id, "secret": share.secret},
                )

                expire_date = datetime.strftime(expire_date, "%b %m, %Y")
                response = {
                    "status": "success",
                    "days": days,
                    "expire": expire_date,
                    "link": link,
                }
            except:
                response = {"status": "error", "days": days}

        return JsonResponse(response)

    return JsonResponse({"error": "You are not allowed to perform this action."})
