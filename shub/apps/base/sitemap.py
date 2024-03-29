"""

Copyright 2017-2023 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""


from django.contrib.sitemaps import Sitemap

from shub.apps.main.models import Collection, Container


class BaseSitemap(Sitemap):
    priority = 0.5

    def location(self, obj):
        return obj.get_absolute_url()


class ContainerSitemap(BaseSitemap):
    changefreq = "weekly"

    def lastmod(self, obj):
        return obj.build_date

    def items(self):
        return [x for x in Container.objects.all() if x.collection.private is False]


class CollectionSitemap(BaseSitemap):
    changefreq = "weekly"

    def lastmod(self, obj):
        return obj.modify_date

    def items(self):
        return [x for x in Collection.objects.all() if x.private is False]
