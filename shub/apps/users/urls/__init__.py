from .social import urlpatterns as socialurls
from .teams import urlpatterns as team_urls
from .users import urlpatterns as userurls

urlpatterns = socialurls + userurls + team_urls
