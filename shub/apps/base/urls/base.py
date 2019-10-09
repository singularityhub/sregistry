'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from django.views.generic.base import TemplateView
from django.conf.urls import url
import shub.apps.base.views as views

urlpatterns = [
  
    # Assets, e.g., /assets/config/config.prod.json
    url(r'^assets/config/config.prod.json$', views.config_prod_json, name="config.prod.json"),
  
    url(r'^$', views.index_view, name="index"),
    url(r'^about$', views.about_view, name="about"),
    url(r'^tools$', views.tools_view, name="tools"),
    url(r'^terms$', views.terms_view, name="terms"),
    url(r'^robots\.txt/$', TemplateView.as_view(template_name='base/robots.txt', 
                                                content_type='text/plain')),
]
