from django.conf import settings

from shub.logger import bot

# Ensure that application credentials exist
for required in [
    "GOOGLE_APPLICATION_CREDENTIALS",
    "GOOGLE_PROJECT",
    "GOOGLE_BUILD_EXPIRE_SECONDS",
]:
    if not hasattr(settings, required):
        bot.exit("%s not defined in secrets." % required)
