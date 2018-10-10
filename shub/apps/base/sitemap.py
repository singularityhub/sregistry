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


from django.contrib.sitemaps import Sitemap
from shub.apps.main.models import (
    Container, 
    Collection
)

class BaseSitemap(Sitemap):
    priority = 0.5

    def location(self,obj):
        return obj.get_absolute_url()


class ContainerSitemap(BaseSitemap):
    changefreq = "weekly"

    def lastmod(self,obj):
        return obj.build_date

    def items(self):
        return [x for x in Container.objects.all() if x.collection.private == False]

class CollectionSitemap(BaseSitemap):
    changefreq = "weekly"

    def lastmod(self,obj):
        return obj.modify_date

    def items(self):
        return [x for x in Collection.objects.all() if x.private == False]
