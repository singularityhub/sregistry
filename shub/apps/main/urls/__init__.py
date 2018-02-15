from .containers import urlpatterns as container_urls
from .collections import urlpatterns as collection_urls
from .compare import urlpatterns as compare_urls
from .demos import urlpatterns as demo_urls
from .tags import urlpatterns as tag_urls
from .labels import urlpatterns as label_urls

urlpatterns =  collection_urls + container_urls + compare_urls + demo_urls + tag_urls + label_urls
