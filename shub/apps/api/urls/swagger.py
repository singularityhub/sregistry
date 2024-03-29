"""

Copyright 2017-2023 Vanessa Sochat

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.urls import re_path
from rest_framework_swagger.views import get_swagger_view

swagger_view = get_swagger_view(title="Singularity Registry API", url="")

urlpatterns = [re_path(r"^$", swagger_view)]
