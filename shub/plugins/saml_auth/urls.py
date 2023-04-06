"""

Copyright 2017-2023 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.urls import re_path

import shub.plugins.saml_auth.views as views

urlpatterns = [re_path(r"^saml.xml$", views.saml_metadata_view, name="samlxml")]
