from django.urls import re_path

from shub.plugins.globus import views

urlpatterns = [
    re_path(r"^login/$", views.globus_login, name="globus_login"),
    re_path(r"^logout/$", views.globus_logout, name="globus_logout"),
    re_path(r"^transfer$", views.globus_transfer, name="globus_transfer"),
    re_path(
        r"^endpoint/(?P<endpoint_id>.+?)/(?P<cid>\d+)?$",
        views.globus_endpoint,
        name="globus_endpoint",
    ),
    re_path(
        r"^endpoint/(?P<cid>\d+)/?$", views.globus_endpoint, name="globus_endpoint"
    ),
    re_path(
        r"^transfer/(?P<cid>\d+)/?$", views.globus_transfer, name="globus_transfer"
    ),
    re_path(
        r"^transfer/(?P<endpoint>.+?)/container/(?P<cid>\d+)/?$",
        views.submit_transfer,
        name="submit_transfer",
    ),
]
