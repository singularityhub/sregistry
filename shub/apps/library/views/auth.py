"""

Copyright (C) 2019-2021 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from shub.apps.users.models import User

from .helpers import validate_token, generate_user_data, get_token


class TokenStatusView(APIView):
    """Given a GET request with a token, return if valid."""

    renderer_classes = (JSONRenderer,)

    def get(self, request, format=None):
        if validate_token(request):
            return Response(status=200)
        return Response(status=404)


class GetNamedEntityView(APIView):
    """Given a request for an entity, return the response"""

    renderer_classes = (JSONRenderer,)

    def get(self, request, username):

        print("GET NamedEntityView")
        print(request.query_params)
        print(username)

        token = validate_token(request)
        if token:

            # Look up the user, must exist with the token
            try:
                user = User.objects.get(username=username)
            except:
                return Response(status=404)

            # Verify that the token belongs to the user
            token = get_token(request)

            if token.user != user:
                return Response(status=404)

            # Generate user data
            data = generate_user_data(user)

            return Response(data={"data": data}, status=200)
        return Response(status=404)


class GetEntitiesView(APIView):
    """I'm not sure the purpose of this endpoint."""

    renderer_classes = (JSONRenderer,)

    def get(self, request, format=None):

        print("GET GetEntitiesView")

        if validate_token(request):

            print("TOKEN IS VALID")
            token = get_token(request)

            # Generate user data
            data = {"data": generate_user_data(token.user)}
            return Response(data=data, status=200)

        return Response(status=404)
