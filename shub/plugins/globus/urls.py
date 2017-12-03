from django.conf.urls import url
from shub.plugins.globus import views

urlpatterns = [
    url(r'^login/$', views.globus_login, name="globus_login"),
    url(r'^transfer$', views.globus_transfer, name="globus_transfer"),
]

