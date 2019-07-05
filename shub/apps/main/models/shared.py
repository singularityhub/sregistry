'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from django.conf import settings
from django.urls import reverse
from django.db import models
from django.contrib.postgres.fields import JSONField
from taggit.managers import TaggableManager

import uuid

from .helpers import (
    has_view_permission, 
    has_edit_permission,
    get_collection_users
)


################################################################################
# Supporting Variables and Functions ###########################################
################################################################################


PRIVACY_CHOICES = ((False, 'Public (The collection will be accessible by anyone)'),
                   (True, 'Private (The collection will be not listed.)'))


def get_privacy_default():
    if settings.PRIVATE_ONLY is True:
        return settings.PRIVATE_ONLY
    return settings.DEFAULT_PRIVATE


################################################################################
# Collections ##################################################################
#########################################b######################################

class Collection(models.Model):
    '''A container collection is a build (multiple versions of the same image) created by an owner,
    with other possible contributors
    '''

    # Container Collection Descriptors
    name = models.CharField(max_length=250,  # name of registry collection
                            unique=True,     # eg, tensorflow <-- /tensorflow
                            blank=False,     # corresponding to a folder, eg tensorflow
                            null=False)
                                        
    add_date = models.DateTimeField('date published', auto_now_add=True)
    modify_date = models.DateTimeField('date modified', auto_now=True)
    secret = models.CharField(max_length=200, null=False, verbose_name="Collection secret for webhook")
    metadata = JSONField(default=dict) # open field for metadata about a collection
    tags = TaggableManager()

    # Users
    owners = models.ManyToManyField('users.User', blank=True, default=None,
                                     related_name="container_collection_owners",
                                     related_query_name="owners")

    contributors = models.ManyToManyField('users.User',
                                          related_name="container_collection_contributors",
                                          related_query_name="contributor", 
                                          blank=True,
                                          help_text="users with edit permission to the collection",
                                          verbose_name="Contributors")
    
    # By default, collections are public
    private = models.BooleanField(choices=PRIVACY_CHOICES, 
                                  default=get_privacy_default,
                                  verbose_name="Accessibility")
    
    def get_absolute_url(self):
        return_cid = self.id
        return reverse('collection_details', args=[str(return_cid)])

    def __str__(self):
        return self.get_uri()

    def __unicode__(self):
        return self.get_uri()

    def sizes(self, container_name=None):
        '''return list of sizes for containers across collection.
           Optionally limited to container name'''
        if container_name is not None:
            queryset = self.containers.filter(name=container_name)
        else:
            queryset = self.containers.all()
        return [x.metadata['size_mb'] for x in queryset if 'size_mb' in x.metadata]


    def members(self):
        '''a compiled list of members (contributors and owners)
        '''
        return get_collection_users(self)


    def mean_size(self, container_name=None):
        total = self.total_size(container_name=container_name)
        if total == 0:
            return total
        return total / self.containers.count()

    def total_size(self, container_name=None):
        sizes = self.sizes(container_name=container_name)
        return sum(sizes)

    def get_uri(self):
        return "%s:%s" %(self.name,
                         self.containers.count())

    def get_label(self):
        return "collection"


    def labels(self):
        '''return common *shared* collection labels'''
        return Label.objects.filter(containers__in=self.containers.all()).distinct()


    def container_names(self):
        '''return distinct container names'''
        return list([x[0] for x in self.containers.values_list('name').distinct() if len(x) > 0])
   
    # Permissions

    def has_edit_permission(self, request):
        '''can the user of the request edit the collection
        '''
        return has_edit_permission(request=request,
                                   instance=self)


    def has_view_permission(self, request):
        '''can the user of the request view the collection
        '''
        return has_view_permission(request=request,
                                   instance=self)



    def has_collection_star(self, request):
        '''returns true or false to indicate
           if a user has starred a collection
        '''
        if request.user.is_authenticated:
            try:
                Star.objects.get(user=request.user,
                                 collection=self)
                return True 
            except:
                return False
        return False


    class Meta:
        app_label = 'main'
        permissions = (
            ('pull_collection', 'Pull container collection'),
            ('change_privacy_collection', 'Change the privacy of a collection'),
            ('push_collection', 'Push container collection')
        )


#################################################################################
# Ratings and Sharing ###########################################################
#################################################################################


class Star(models.Model):
    '''a user can star a particular collection
    '''
    # When the user or Collection is deleted, also delete the Stars
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)

    def get_label(self):
        return "collection"

    class Meta:
        unique_together = ('user', 'collection',)
        app_label = 'main'



class Share(models.Model):
    '''a temporary share / link for a container
    '''
    # When the Container is deleted, also delete the share
    container = models.ForeignKey("main.Container", on_delete=models.CASCADE)
    expire_date = models.DateTimeField('share expiration date')
    secret = models.CharField(max_length=250, null=True, blank=True)

    def generate_secret(self):
        self.secret = str(uuid.uuid4())

    def save(self, *args, **kwargs):
        if self.secret in ['', None]:
            self.generate_secret()
        super(Share, self).save(*args, **kwargs)

    def __str__(self):
        return self.container.name

    def get_label(self):
        return "main"

    class Meta:
        unique_together = ('expire_date', 'container',)
        app_label = 'main'



################################################################################
# Label ########################################################################
################################################################################


class Label(models.Model):
    '''A label is extracted from the Singularity build specification to describe a container
    '''
    key = models.CharField(max_length=250, null=False, blank=False)
    value = models.CharField(max_length=250, null=False, blank=False)
    containers = models.ManyToManyField('main.Container',
                                         blank=False,
                                         related_name='containers')

    def __str__(self):
        return "%s:%s" %(self.key, self.value)

    def __unicode__(self):
        return "%s:%s" %(self.key, self.value)

    def get_label(self):
        return "label"

    class Meta:
        app_label = 'main'
        unique_together = (("key", "value"),)
