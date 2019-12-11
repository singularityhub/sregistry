from django.conf.urls import url
from shub.plugins.globus import views

urlpatterns = [
    url(r"^login/$", views.globus_login, name="globus_login"),
    url(r"^logout/$", views.globus_logout, name="globus_logout"),
    url(r"^transfer$", views.globus_transfer, name="globus_transfer"),
    url(
        r"^endpoint/(?P<endpoint_id>.+?)/(?P<cid>\d+)?$",
        views.globus_endpoint,
        name="globus_endpoint",
    ),
    url(r"^endpoint/(?P<cid>\d+)/?$", views.globus_endpoint, name="globus_endpoint"),
    url(r"^transfer/(?P<cid>\d+)/?$", views.globus_transfer, name="globus_transfer"),
    url(
        r"^transfer/(?P<endpoint>.+?)/container/(?P<cid>\d+)/?$",
        views.submit_transfer,
        name="submit_transfer",
    ),
]
