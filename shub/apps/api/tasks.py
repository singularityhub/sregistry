"""

Copyright (C) 2017-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from shub.logger import bot


def expire_share(sid):
    """expire a share based on its id, meaning deleting it so that
    it can no longer be used.

    Parameters
    ==========
    sid: the share id to expire
    """
    from shub.apps.main.models import Share

    try:
        share = Share.objects.get(id=sid)
        share.delete()
    except Share.DoesNotExist:
        bot.warning("Share %s expired." % sid)
