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
    '''Log an API request based on user, view, etc.
    '''
    user = models.ForeignKey(settings.AUTH_USER_MODEL, 
                             null=True, blank=True, 
                             on_delete=models.CASCADE)

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


class APIRequestCount(models.Model):
    ''' Keep track of a count of requests based on path and
        view type, for quick querying later
    '''
    from shub.apps.main.models import Collection

    # When the collection is deleted, the count is deleted too
    collection = models.ForeignKey(Collection,
                                   default=None, 
                                   blank=False, 
                                   null=True, 
                                   on_delete=models.CASCADE)

    count = models.PositiveIntegerField(default=0)
    path = models.CharField(max_length=200, db_index=True)
    method = models.CharField(max_length=200, db_index=True)
 
    class Meta:
        verbose_name = 'Container Request Counter'

    def __str__(self):
        return '%s %s: %s' %(self.method, 
                             self.collection.name,
                             self.count)

                   # BaseAPIRequestLog (instance)
def finalize_request(sender, instance, **kwargs):
    '''finalize request will add a counter object for the collection,
       method, and path
    '''
    from shub.apps.logs.utils import get_request_collection

    try:
        collection = get_request_collection(instance)
    except:
        collection = None    

    if collection is not None:    
        counter, _ = APIRequestCount.objects.get_or_create(path=instance.view,
                                                           method=instance.view_method,
                                                           collection=collection)
        counter.count += 1
        counter.save()

    # Clear the response, we've saved minimal detail
    if settings.LOGGING_SAVE_RESPONSES is False:
        instance.response = {}


pre_save.connect(finalize_request, sender=APIRequestLog)
