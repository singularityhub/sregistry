from .swagger import urlpatterns as swagger_urls
from .routers import urlpatterns as routers
from .collections import urlpatterns as collection_urls
from .containers import urlpatterns as container_urls
from .labels import urlpatterns as labels_urls
from .registry import urlpatterns as registry_urls

urlpatterns = (
    swagger_urls
    + routers
    + collection_urls
    + container_urls
    + labels_urls
    + registry_urls
)
