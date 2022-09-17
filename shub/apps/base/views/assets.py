"""

Copyright (C) 2017-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.shortcuts import render
from ratelimit.decorators import ratelimit

from shub.settings import VIEW_RATE_LIMIT as rl_rate
from shub.settings import VIEW_RATE_LIMIT_BLOCK as rl_block


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def config_prod_json(request):
    return render(request, "assets/config.prod.json")
