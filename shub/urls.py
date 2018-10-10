'''

Copyright (C) 2017-2018 Vanessa Sochat.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

'''

from importlib import import_module

from django.conf.urls import include, url
from shub.apps.base import urls as base_urls
from shub.apps.main import urls as main_urls
from shub.apps.users import urls as user_urls
from shub.apps.api import urls as api_urls

from django.contrib import admin
from django.contrib.sitemaps.views import sitemap, index

from django.conf import settings


# Configure custom error pages
from django.conf.urls import ( handler404, handler500 )
handler404 = 'shub.apps.base.views.handler404'
handler500 = 'shub.apps.base.views.handler500'

# Sitemaps
from shub.apps.base.sitemap import (
    CollectionSitemap, 
    ContainerSitemap
)

sitemaps = {"containers":ContainerSitemap,
            "collections":CollectionSitemap}

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include(base_urls)),
    url(r'^api/', include(api_urls)),
    url(r'^', include(main_urls)),
    url(r'^', include(user_urls)),
    url(r'^sitemap\.xml$', index, {'sitemaps': sitemaps}, name="sitemap"),
    url(r'^sitemap-(?P<section>.+)\.xml$', sitemap, {'sitemaps': sitemaps}),
]

# Load URLs for any enabled plugins
for plugin in settings.PLUGINS_ENABLED:
    urls_module = 'shub.plugins.' + plugin + '.urls'
    plugin_urls = import_module(urls_module)
    url_regex = '^' + plugin + '/'
    urlpatterns.append(url(url_regex, include(plugin_urls)))
