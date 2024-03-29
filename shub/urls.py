"""

Copyright 2017-2023 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from importlib import import_module

from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import index, sitemap
from django.urls import include, re_path
from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view

from shub.apps.api import urls as api_urls
from shub.apps.base import urls as base_urls
from shub.apps.base.sitemap import CollectionSitemap, ContainerSitemap
from shub.apps.library import urls as library_urls
from shub.apps.main import urls as main_urls
from shub.apps.users import urls as user_urls

# Documentation URL
API_TITLE = "Singularity Registry API"
API_DESCRIPTION = "Open Source Container Registry API"
schema_view = get_schema_view(title=API_TITLE)

# Configure custom error pages
handler404 = "shub.apps.base.views.handler404"
handler500 = "shub.apps.base.views.handler500"

# Sitemaps
sitemaps = {"containers": ContainerSitemap, "collections": CollectionSitemap}

urlpatterns = [
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^", include(base_urls)),
    re_path(r"^api/", include(api_urls)),
    re_path(
        r"^", include(library_urls)
    ),  # Sylabs library API - includes v1 and v2 (damn)
    re_path(r"^api/schema/$", schema_view),
    re_path(
        r"^api/docs/", include_docs_urls(title=API_TITLE, description=API_DESCRIPTION)
    ),
    re_path(r"^", include(main_urls)),
    re_path(r"^", include(user_urls)),
    re_path(r"^sitemap\.xml$", index, {"sitemaps": sitemaps}, name="sitemap"),
    re_path(r"^sitemap-(?P<section>.+)\.xml$", sitemap, {"sitemaps": sitemaps}),
    re_path(r"^django-rq/", include("django_rq.urls")),
]

# Load URLs for any enabled plugins
for plugin in settings.PLUGINS_ENABLED:
    urls_module = "shub.plugins." + plugin + ".urls"
    plugin_urls = import_module(urls_module)

    url_regex = "^" + plugin + "/"

    # per protocol, keystore must be /pks
    if plugin == "pgp":
        url_regex = "^pks/"
    urlpatterns.append(re_path(url_regex, include(plugin_urls)))
