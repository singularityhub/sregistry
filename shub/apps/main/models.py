'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017 Vanessa Sochat.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from shub.settings import (
    MEDIA_ROOT,
    PRIVATE_ONLY, 
    DEFAULT_PRIVATE
)
from shub.apps.api.models import ImageFile
from shub.apps.users.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q, DO_NOTHING
from django.db.models.signals import post_delete, pre_delete
from django.db.models import Avg, Sum

from django.contrib.postgres.fields import JSONField
from polymorphic.models import PolymorphicModel
from taggit.managers import TaggableManager

import collections
import operator
import uuid
import os
import re
from urllib import parse

#######################################################################################################
# Supporting Variables and Functions ##################################################################
#######################################################################################################


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
    if PRIVATE_ONLY is True:
        return PRIVATE_ONLY
    return DEFAULT_PRIVATE


def has_edit_permission(instance,request):
    '''can the user of the request edit the collection or container?
    '''
    if request.user.is_authenticated() is False:
        return False

    # Global Admins
    if request.user.admin is True:
        return True

    if request.user.is_superuser is True:
        return True

    # Collection Contributors
    contributors = get_collection_users(instance)
    if request.user in contributors:
        return True
    return False


def has_view_permission(instance,request):
    '''can the user of the request edit the collection or container?
    '''
    if isinstance(instance, Container):
        instance = instance.collection

    if instance.private is False:
        return True

    if request.user.is_authenticated() is False:
        return False
        
    # Global Admins
    if request.user.admin is True or request.user.is_superuser:
        return True

    # Collection Contributors
    contributors = get_collection_users(instance)
    if request.user in contributors:
        return True

    return False



def delete_imagefile(sender,instance,**kwargs):
    if instance.image not in ['',None]:
        if hasattr(instance.image,'datafile'):
            instance.image.datafile.delete()

#######################################################################################################
# Collections #########################################################################################
#######################################################################################################

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
    metadata = JSONField(default={}) # open field for metadata about a collection

    # Users
    owner = models.ForeignKey('users.User', blank=True, default=None, null=True)
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


    def has_view_permission(self,request):
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
            ('del_container_collection', 'Delete container collection'),
            ('edit_container_collection', 'Edit container collection')
        )



#######################################################################################################
# Containers ##########################################################################################
#######################################################################################################

class Container(models.Model):
    '''A container is a base (singularity) container, stored as a file (image) with a unique id and name
    '''
    add_date = models.DateTimeField('date container added', auto_now=True)
    collection = models.ForeignKey('main.Collection',null=False,blank=False, related_name="containers")
    image = models.ForeignKey(ImageFile, null=True, blank=False) # an image upload, or maybe change it?
    metadata = JSONField(default={},blank=True)
    metrics = JSONField(default={},blank=True)
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


class Demo(models.Model):
    '''A demo is an supplementary materil (asciicast, youtube video, or other) provided by a user.
    '''
    description = models.CharField(max_length=250,null=False,blank=False)
    creation_date = models.DateTimeField('date demo created', auto_now=True)
    collection = models.ForeignKey(Collection,null=False,blank=False)
    kind = models.CharField(max_length=250,choices=DEMO_KINDS)
    url = models.CharField(max_length=250,null=False,blank=False,
                           help_text="URL for an asciicast, video, or other kind of documentation.")
    tags = TaggableManager()

    class Meta:
        app_label = 'main'
 
    def get_absolute_url(self):
        return_id = self.id
        return reverse('view_demo', args=[str(return_id)])


#################################################################################
# Ratings and Sharing ###########################################################
#################################################################################


class Star(models.Model):
    '''a user can star a particular collection
    '''
    user = models.ForeignKey('users.User')
    collection = models.ForeignKey(Collection)

    def get_label(self):
        return "collection"

    class Meta:
        unique_together = ('user','collection',)
        app_label = 'main'



class Share(models.Model):
    '''a temporary share / link for a container
    '''
    container = models.ForeignKey(Container)
    expire_date = models.DateTimeField('share expiration date')
    secret = models.CharField(max_length=250,null=True,blank=True)

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



#######################################################################################################
# Label ###############################################################################################
#######################################################################################################


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
