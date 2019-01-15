from shub.settings import SREGISTRY_CUSTOM_STORAGE
from django.db.models.signals import pre_delete

# Import Container and Collection bases based on client storage

from .containers import Container

if SREGISTRY_CUSTOM_STORAGE==False:
    from .containers import delete_imagefile
    pre_delete.connect(delete_imagefile, sender=Container)    
else:
    from .containers import delete_remotefile
    pre_delete.connect(delete_remotefile, sender=Container)    

from .shared import *
