from django.conf.urls import url
#from rest_framework.routers import DefaultRouter

from shub.apps.library import views

# Create a router and register our viewsets with it.
#router = DefaultRouter()
#router.register(r'images', views.ImageViewSet)

# The patterns here are prefixed with v2/
urlpatterns = [
    url(r'^images/(?P<name>.+?)/?$', views.GetImageView.as_view()),
    url(r'^imagefile/(?P<name>.+?)/?$', views.DownloadImageView.as_view()),
    url(r'^$', views.LibraryBaseView.as_view())
#    url(r'^', include(router.urls)),
]
