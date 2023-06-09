from django.core.management.base import BaseCommand

import shub.settings as cfg


class Command(BaseCommand):
    requires_system_checks = []
    help = """Show configured setting"""

    def add_arguments(self, parser):
        parser.add_argument("setting", nargs="*")

    def handle(self, *args, **kwargs):
        # Either dump all settings, or just the ones specified on the command line
        if len(kwargs["setting"]) == 0:
            for key, val in cfg.__dict__.items():
                if key.isupper():
                    print(key, "=", val)
        else:
            for i in kwargs["setting"]:
                if i in dir(cfg):
                    print(i, "=", cfg.__dict__[i])
