'''

Copyright (C) 2017-2019 Vanessa Sochat.

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

from django.conf.urls import ( url, include )
import rest_framework.authtoken.views as authviews

from rest_framework import routers

from shub.apps.api.urls.containers import ContainerViewSet
from shub.apps.api.urls.collections import CollectionViewSet
from shub.apps.api.actions.push import collection_auth_check
from shub.apps.api.actions.upload import (
    UploadUI,
    upload_complete
)

router = routers.DefaultRouter()
router.register(r'^containers', ContainerViewSet, base_name="container")
router.register(r'^collections', CollectionViewSet, base_name="collection")

urlpatterns = [

    url(r'^', include(router.urls)),

    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', authviews.obtain_auth_token ),

    url(r'^upload/chunked_upload/?$', collection_auth_check, name='collection_auth_check'),
    url(r'^upload/(?P<cid>.+?)/?$', UploadUI.as_view(), name='chunked_upload'),
    url(r'^uploads/complete/?$', upload_complete, name='terminal_upload_complete'),

]
