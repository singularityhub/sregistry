'''

Adopted from drf-tracking
https://github.com/aschn/drf-tracking

'''

from django.db import models


class PrefetchUserManager(models.Manager):
    def get_queryset(self):
        return super(PrefetchUserManager, self).get_queryset().select_related('user')
