"""

Copyright (C) 2017-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.shortcuts import render

from ratelimit.decorators import ratelimit

from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from shub.settings import VIEW_RATE_LIMIT as rl_rate, VIEW_RATE_LIMIT_BLOCK as rl_block


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def index_view(request):
    return render(request, "main/index.html")


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def about_view(request):
    return render(request, "main/about.html")


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def tools_view(request):
    return render(request, "main/tools.html")


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def terms_view(request):
    return render(request, "terms/usage_agreement.html")


class VersionView(APIView):
    """{'data': {'version': 'v1.0.4-0-g24d3b74', 'apiVersion': '2.0.0-alpha.2'}}    
    """

    renderer_classes = (JSONRenderer,)

    def get(self, request):

        data = {"version": "v1.0.0", "apiVersion": "2.0.0-alpha.1"}

        return Response(data={"data": data}, status=200)
