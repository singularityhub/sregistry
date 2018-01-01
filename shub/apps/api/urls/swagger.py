'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017 Vanessa Sochat.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from django.views.generic.base import TemplateView
from django.conf.urls import url 

from rest_framework_swagger.views import get_swagger_view
swagger_view = get_swagger_view(title='Singularity Registry API',url='')

urlpatterns = [
    url(r'^$', swagger_view)
]
