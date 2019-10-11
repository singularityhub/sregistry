from django.conf.urls import url
#from rest_framework.routers import DefaultRouter

from shub.apps.library import views

# Create a router and register our viewsets with it.
#router = DefaultRouter()
#router.register(r'images', views.ImageViewSet)

# The patterns here are prefixed with v1/

urlpatterns = [


    # /v1/images/vsoch/dinosaur-collection/another:sha256.b80bddda1d84d827ea135eb890f969a83ccba2a7a2152e15567d114857280120
    url(r'^v1/images/(?P<username>.+?)/(?P<collection>.+?)/(?P<name>.+?):(?P<version>.+?)$', views.PushImageView.as_view()),

    url(r'^v1/images/(?P<name>.+?)/?$', views.GetImageView.as_view()),

    url(r'^v2/imagefile/(?P<container_id>.+?)/?$', views.RequestPushImageFileView.as_view()), # return push url

    #TODO need to implement this view to complete (adding tag maybe?)
    url(r'^v2/imagefile/(?P<container_id>.+?)/_complete?$', views.CompletePushImageFileView.as_view()),
    url(r'^v2/push/imagefile/(?P<container_id>.+?)/(?P<secret>.+?)?$', 
        views.PushImageFileView.as_view(), name="PushImageFileView"), # push image

    url(r'^v1/imagefile/(?P<name>.+?)/?$', views.DownloadImageView.as_view()), # not sure this is used

    url(r'^v1/token-status$', views.TokenStatusView.as_view()),

    url(r'^v1/collections/(?P<username>.+?)/(?P<name>.+?)$', views.GetNamedCollectionView.as_view()),  # collection with username
    url(r'^v1/collections$', views.CollectionsView.as_view()),

    url(r'^v1/containers/(?P<username>.+?)/(?P<name>.+?)/(?P<container>.+?)$', views.GetNamedContainerView.as_view()), # and container
    url(r'^v1/containers$', views.ContainersView.as_view()),

    url(r'^v1/entities/(?P<username>.+?)/?$', views.GetNamedEntityView.as_view()),
    url(r'^v1/entities/?$', views.GetEntitiesView.as_view()),

    url(r'^v1/$', views.LibraryBaseView.as_view())

]


#singularity push -U --library http://127.0.0.1 busybox_latest.sif library://vsoch/dinosaur-collection/container:tag
