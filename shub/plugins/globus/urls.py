from django.conf.urls import url
from shub.plugins.globus import views

urlpatterns = [
    url(r'^login/$', views.globus_login, name="globus_login"),
    url(r'^logout/$', views.globus_logout, name="globus_logout"),
    url(r'^transfer$', views.globus_transfer, name="globus_transfer"),
]

