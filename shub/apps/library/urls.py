from django.conf.urls import url
#from rest_framework.routers import DefaultRouter

from shub.apps.library import views

# Create a router and register our viewsets with it.
#router = DefaultRouter()
#router.register(r'images', views.ImageViewSet)

# The patterns here are prefixed with v1/

urlpatterns = [


    url(r'^images/(?P<name>.+?)/?$', views.GetImageView.as_view()),
    url(r'^imagefile/(?P<name>.+?)/?$', views.DownloadImageView.as_view()),
    url(r'^token-status$', views.TokenStatusView.as_view()),
    url(r'^collections/(?P<username>.+?)/(?P<name>.+?)$', views.GetNamedCollectionView.as_view()),
    url(r'^collections$', views.CollectionsView.as_view()),
    url(r'^entities/(?P<username>.+?)/?$', views.GetNamedEntityView.as_view()),
    url(r'^entities/?$', views.GetEntitiesView.as_view()),
 
    # TODO: the endpoint here should exist to create the container
    #/v1/containers/vsoch/dinosaur-collection/container

    url(r'^$', views.LibraryBaseView.as_view())
#    url(r'^', include(router.urls)),
]
