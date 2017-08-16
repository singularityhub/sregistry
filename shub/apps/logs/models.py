'''

Adopted from drf-tracking
https://github.com/aschn/drf-tracking

'''

from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save
from django.utils.six import python_2_unicode_compatible
from shub.apps.logs.managers import PrefetchUserManager


@python_2_unicode_compatible
class BaseAPIRequestLog(models.Model):
    '''Log an API request based on user, view, etc.'''
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    requested_at = models.DateTimeField(db_index=True)
    response = models.TextField()
    response_ms = models.PositiveIntegerField(default=0)
    path = models.CharField(max_length=200, db_index=True)
    view = models.CharField(max_length=200, db_index=True)
    view_method = models.CharField(max_length=200, db_index=True)
    remote_addr = models.GenericIPAddressField()
    host = models.URLField()
    method = models.CharField(max_length=10)
    query_params = models.TextField(null=True, blank=True)
    data = models.TextField(null=True, blank=True)
    errors = models.TextField(null=True, blank=True)
    status_code = models.PositiveIntegerField(null=True, blank=True)
    objects = PrefetchUserManager()

    class Meta:
        abstract = True
        verbose_name = 'API Request Log'

    def __str__(self):
        return '{} {}'.format(self.method, self.path)


class APIRequestLog(BaseAPIRequestLog):
    pass


                   # BaseAPIRequestLog (instance)
def remove_response(sender, instance, **kwargs):
    print(instance.response)
    instance.response = None
    instance.save()

# TODO: need to 1) parse container from req.response, then 2) clean the request, then 3) add variable to index
pre_save.connect(remove_response, sender=BaseAPIRequestLog)
