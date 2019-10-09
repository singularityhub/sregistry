'''

Copyright (C) 2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

class TokenStatusView(APIView):
    '''Given a GET request with a token, return if valid.
    '''
    renderer_classes = (JSONRenderer,)
    def get(self, request, format=None):

        token = request.META.get("HTTP_AUTHORIZATION")
        if token:
            try:
                Token.objects.get(key=token.replace("Bearer", "").strip())
            except Token.DoesNotExist:
                return Response(status=404)  
            return Response(status=200)
        return Response(status=404)
