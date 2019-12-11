"""

Copyright (C) 2017-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.http import HttpResponse
from django.urls import reverse
from social_django.utils import load_strategy, load_backend

from ratelimit.decorators import ratelimit

from shub.settings import VIEW_RATE_LIMIT as rl_rate, VIEW_RATE_LIMIT_BLOCK as rl_block

# SAML Authentication


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def saml_metadata_view(request):
    complete_url = reverse("social:complete", args=("saml",))
    saml_backend = load_backend(
        load_strategy(request), "saml", redirect_uri=complete_url
    )
    metadata, errors = saml_backend.generate_metadata_xml()
    if not errors:
        return HttpResponse(content=metadata, content_type="text/xml")
