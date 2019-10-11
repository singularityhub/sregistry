'''

Copyright (C) 2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

class LibraryBaseView(APIView):
    '''The base /v2/ api response, is expected to function as follows:

      GET of /v2 returned 200 OK response
      GET of /v2 has header "Docker-Distribution-API-Version":"registry/2.0"
    '''
    renderer_classes = (JSONRenderer,)
    def get(self, request):

        user = None
        if not request.user.is_anonymous:
            user = request.user.username

        data = {"version":"v1.0.0",
                "apiVersion":"2.0.0-alpha.1",
                "user": user}

        return Response(data=data, status=200)

