"""

Copyright 2017-2023 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.urls import re_path
from django.views.generic.base import TemplateView

import shub.apps.base.views as views

urlpatterns = [
    # Assets, e.g., /assets/config/config.prod.json
    re_path(
        r"^assets/config/config.prod.json$",
        views.config_prod_json,
        name="config.prod.json",
    ),
    re_path(r"^$", views.index_view, name="index"),
    re_path(r"^about$", views.about_view, name="about"),
    re_path(r"^version$", views.VersionView.as_view(), name="version"),
    re_path(r"^tools$", views.tools_view, name="tools"),
    re_path(r"^terms$", views.terms_view, name="terms"),
    re_path(
        r"^robots\.txt/$",
        TemplateView.as_view(
            template_name="base/robots.txt", content_type="text/plain"
        ),
    ),
]
