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
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
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

urlpatterns = [

    # Share
    url(r'^containers/(?P<cid>\d+)/download/share/(?P<secret>.+?)$', views.download_share,name='download_share'),
    url(r'^containers/(?P<cid>\d+)/share$', views.generate_share,name='generate_share'),
 
    # Containers
    url(r'^tags/(?P<tid>.+?)/view$', views.view_tag,name='view_tag'),
    url(r'^containers/(?P<cid>\d+)/view$', views.view_container,name='view_container'),
    url(r'^containers/(?P<collection>.+?)/(?P<name>.+?):(?P<tag>.+?)$', views.view_named_container,name='view_container'),
    url(r'^containers/(?P<cid>\d+)/$', views.container_details,name='container_details'),
    url(r'^containers/(?P<cid>\d+)/tags$', views.container_tags,name='container_tags'),
    url(r'^containers/(?P<cid>\d+)/delete$', views.delete_container,name='delete_container'),
    url(r'^containers/(?P<cid>\d+)/freeze$', views.change_freeze_status,name='change_freeze_status'),

    # Download
    url(r'^containers/(?P<cid>\d+)/download/recipe$', views.download_recipe,name='download_recipe'),
    url(r'^containers/(?P<cid>\d+)/download/(?P<secret>.+?)$', views.download_container,name='download_container'),

]

