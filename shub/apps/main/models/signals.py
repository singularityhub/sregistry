"""

Copyright (C) 2020-2021 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django.db.models.signals import post_delete
from django.dispatch import receiver

from .containers import Container


@receiver(post_delete, sender=Container)
def delete_imagefile(sender, instance, **kwargs):
    print("Delete imagefile signal running.")
    if instance.image not in ["", None]:
        if hasattr(instance.image, "datafile"):
            count = Container.objects.filter(
                image__datafile=instance.image.datafile
            ).count()
            if count == 0:
                print("Deleting %s, no longer used." % instance.image.datafile)
                instance.image.datafile.delete()
