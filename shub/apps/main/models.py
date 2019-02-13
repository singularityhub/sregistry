'''

Copyright (C) 2017-2019 Vanessa Sochat.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

'''

from django.conf import settings
from shub.apps.api.models import ImageFile
from shub.apps.users.models import User
from django.urls import reverse
from django.db import models
from django.db.models import Q, DO_NOTHING
from django.db.models.signals import post_delete, pre_delete
from django.db.models import Avg, Sum
from itertools import chain

from django.contrib.postgres.fields import JSONField
from django.http import HttpRequest
from taggit.managers import TaggableManager

import collections
import operator
import uuid
import os
import re
from urllib import parse

################################################################################
# Supporting Variables and Functions ###########################################
################################################################################


PRIVACY_CHOICES = ((False, 'Public (The collection will be accessible by anyone)'),
                   (True, 'Private (The collection will be not listed.)'))

DEMO_KINDS = (("ASCIINEMA", 'Asciinema'),
              ("YOUTUBE", 'YouTube Video'),
              ("DOCS","Link to Docs or tutorial"))

FROZEN_CHOICES = ((True, 'Frozen'),
                  (False, 'Not Frozen'))

ACTIVE_CHOICES = ((True, 'Active'),
                  (False, 'Disabled'))


def get_privacy_default():
    if settings.PRIVATE_ONLY is True:
        return settings.PRIVATE_ONLY
    return settings.DEFAULT_PRIVATE


def has_edit_permission(instance, request):
    '''can the user of the request edit the collection or container?

       Parameters
       ==========
       instance: the container or collection to check
       request: the request with the user object OR the user object

    '''
    if isinstance(instance, Container):
        instance = instance.collection

    user = request
    if isinstance(user, HttpRequest):
        user = request.user

    # Visitor
    if not user.is_authenticated:
        return False

    # Global Admins
    if user.is_staff:
        return True

    if user.is_superuser:
        return True

    # Collection Owners can edit
    if user in instance.owners.all():
        return True
    return False


def has_view_permission(instance, request):
    '''can the user of the request view the collection or container? This
       permission corresponds with being a contributor, and being able to
       pull

       Parameters
       ==========
       instance: the container or collection to check
       request: the request with the user object

    '''
    if isinstance(instance, Container):
        instance = instance.collection

    user = request
    if isinstance(user, HttpRequest):
        user = request.user

    # All public collections are viewable
    if instance.private is False:
        return True

    # At this point we have a private collection
    if not user.is_authenticated():
        return False
        
    # Global Admins and Superusers
    if user.is_staff or user.is_superuser:
        return True

    # Collection Contributors (owners and contributors)
    contributors = instance.members()
    if user in contributors:
        return True

    return False


def get_collection_users(instance):
    '''get_collection_users will return a list of all owners and contributors
        for a collection. The input instance can be a collection or container.

        Parameters
        ==========
        instance: the collection or container object to use

    '''
    collection = instance
    if isinstance(collection, Container):
        collection = collection.collection

    contributors = collection.contributors.all()
    owners = collection.owners.all()
    members = list(chain(contributors, owners))
    return list(set(members))


def delete_imagefile(sender,instance,**kwargs):
    if instance.image not in ['',None]:
        if hasattr(instance.image,'datafile'):
            instance.image.datafile.delete()



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
        return sum(sizes) / len(sizes)


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
        return list([x[0] for x in self.containers.values_list('name').distinct() if len(x)>0])
   
    # Permissions

    def has_edit_permission(self,request):
        '''can the user of the request edit the collection
        '''
        return has_edit_permission(request=request,
                                   instance=self)


    def has_view_permission(self, request):
        '''can the user of the request view the collection
        '''
        return has_view_permission(request=request,
                                   instance=self)



    def has_collection_star(self,request):
        '''returns true or false to indicate
        if a user has starred a collection'''
        has_star = False
        if request.user.is_authenticated():
            try:
                star = Star.objects.get(user=request.user,
                                        collection=self)
                has_star = True 
            except:
                pass
        return has_star



    class Meta:
        app_label = 'main'
        permissions = (
            ('pull_collection', 'Pull container collection'),
            ('change_privacy_collection', 'Change the privacy of a collection'),
            ('push_collection', 'Push container collection')
        )



################################################################################
# Containers ###################################################################
################################################################################

class Container(models.Model):
    '''A container is a base (singularity) container, stored as a file (image) with a unique id and name
    '''
    add_date = models.DateTimeField('date container added', auto_now=True)

    # When the collection is deleted, DO delete the Container object
    collection = models.ForeignKey('main.Collection', null=False,blank=False, 
                                                      related_name="containers", 
                                                      on_delete=models.CASCADE)

    # When the Image File is deleted, don't delete the Container object (can be updated)
    image = models.ForeignKey(ImageFile, null=True, blank=False, on_delete=models.SET_NULL)
    metadata = JSONField(default=dict, blank=True)
    metrics = JSONField(default=dict,blank=True)
    name = models.CharField(max_length=250, null=False, blank=False)
    tag = models.CharField(max_length=250,null=False,blank=False,default="latest")
    secret = models.CharField(max_length=250,null=True,blank=True)
    version = models.CharField(max_length=250,null=True,blank=True)
    tags = TaggableManager()
    frozen = models.BooleanField(choices=FROZEN_CHOICES,
                                 default=False,
                                 verbose_name="is the container frozen, meaning builds will not be replaced?")

    # A container only gets a version when it's frozen, otherwise known by tag
    def get_short_uri(self):
        return "%s/%s:%s" %(self.collection.name,
                            self.name,
                            self.tag)

    def get_uri(self): # shub://username/reponame:branch@tag
        if self.frozen is False:
            return self.get_short_uri()
        version = "%s@%s" %(self.tag,self.version)
        return "%s/%s:%s" %(self.collection.name,
                            self.name,
                            version)

    def update_secret(self,save=True):
        '''secret exists to make brute force download not possible'''
        self.secret = str(uuid.uuid4())
        if save is True:
            self.save()

    def save(self, *args, **kwargs):
        '''update secret on each save'''
        self.update_secret(save=False)
        super(Container, self).save(*args, **kwargs)

    def get_image_path(self):
        if self.image not in [None,""]:
            return self.image.datafile.path
        return None

    def get_download_name(self):
        extension = "img"
        image_path = self.get_image_path()
        if image_path is not None:
            if image_path.endswith('gz'):
                extension = "img.gz"
        return "%s.%s" %(self.get_uri().replace('/','-'), extension)

    def members(self):
        return get_collection_users(self)

    def get_download_url(self):
        if self.image not in [None,""]:
            return self.image.datafile.file
        return None

    def get_label(self):
        return "container"


    def __str__(self):
        return self.get_uri()


    def __unicode__(self):
        return self.get_uri()


    class Meta:
        ordering = ['name']
        app_label = 'main' 
        unique_together =  (("name","tag","collection"),)

    def get_absolute_url(self):
        return_cid = self.id
        return reverse('container_details', args=[str(return_cid)])


    def labels(self):
        return Label.objects.filter(containers=self)
        

    def has_edit_permission(self,request):
        return has_edit_permission(request=request,
                                   instance=self.collection)

    def has_view_permission(self,request):
        return has_view_permission(request=request,
                                   instance=self.collection)



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
        unique_together = ('user','collection',)
        app_label = 'main'



class Share(models.Model):
    '''a temporary share / link for a container
    '''
    # When the Container is deleted, also delete the share
    container = models.ForeignKey(Container, on_delete=models.CASCADE)
    expire_date = models.DateTimeField('share expiration date')
    secret = models.CharField(max_length=250, null=True, blank=True)

    def generate_secret(self):
        self.secret = str(uuid.uuid4())

    def save(self, *args, **kwargs):
        if self.secret in ['',None]:
            self.generate_secret()
        super(Share, self).save(*args, **kwargs)

    def __str__(self):
        return self.container.name

    def get_label(self):
        return "main"

    class Meta:
        unique_together = ('expire_date','container',)
        app_label = 'main'



################################################################################
# Label ########################################################################
################################################################################


class Label(models.Model):
    '''A label is extracted from the Singularity build specification to describe a container
    '''
    key = models.CharField(max_length=250, null=False, blank=False)
    value = models.CharField(max_length=250, null=False, blank=False)
    containers = models.ManyToManyField('main.Container',blank=False, related_name='containers')

    def __str__(self):
        return "%s:%s" %(self.key,self.value)

    def __unicode__(self):
        return "%s:%s" %(self.key,self.value)

    def get_label(self):
        return "label"

    class Meta:
        app_label = 'main'
        unique_together =  (("key","value"),)

pre_delete.connect(delete_imagefile, sender=Container)
