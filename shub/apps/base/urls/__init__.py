from .search import urlpatterns as search_urls
from .base import urlpatterns as base_urls

urlpatterns = base_urls + search_urls
