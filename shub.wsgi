import os

os.environ["DJANGO_SETTINGS_MODULE"] = "shub.settings"
from django.core.wsgi import get_wsgi_application  # noqa

application = get_wsgi_application()
