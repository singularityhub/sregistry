from django.apps import AppConfig


class MainAppConfig(AppConfig):
    name = "shub.apps.main"

    def ready(self):
        import shub.apps.main.models.signals
