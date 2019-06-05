from django.conf import settings
from shub.logger import bot

# Ensure that application credentials exist
for required in ['GOOGLE_APPLICATION_CREDENTIALS', 
                 'SREGISTRY_GOOGLE_PROJECT']:
    if not hasattr(settings, required):
        bot.exit('%s not defined in secrets.' % required)
