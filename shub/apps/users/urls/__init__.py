from .social import urlpatterns as socialurls
from .users import urlpatterns as userurls

urlpatterns = socialurls + userurls
