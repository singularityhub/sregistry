'''

Copyright (c) 2017, Vanessa Sochat, All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THEfc
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''

from django.conf.urls import url
import shub.apps.main.views as views
from shub.apps.main.query import collection_query

urlpatterns = [

    url(r'^collections$', views.all_collections, name="collections"),
    url(r'^collections/(?P<cid>\d+)/edit$',views.edit_collection,name='edit_collection'),
    url(r'^collections/(?P<cid>\d+)/$',views.view_collection,name='collection_details'),
    url(r'^collections/my$',views.my_collections,name='my_collections'),
    url(r'^collections/(?P<cid>\d+)/usage$', views.collection_commands,name='collection_commands'),
    url(r'^collections/(?P<cid>\d+)/delete$', views.delete_collection,name='delete_collection'),
    url(r'^collections/(?P<cid>\d+)/private$',views.make_collection_private,name='make_collection_private'),
    url(r'^collections/(?P<cid>\d+)/public$',views.make_collection_public,name='make_collection_public')

]

