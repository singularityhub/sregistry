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

from shub.apps.api.models import ImageFile
from shub.apps.users.models import User
from django.core.urlresolvers import reverse
from django.db import models

from django.contrib.postgres.fields import JSONField
from taggit.managers import TaggableManager

import uuid
import os
import re
from .helpers import (
    has_view_permission, 
    has_edit_permission,
    get_collection_users
)

################################################################################
# Supporting Variables and Functions ###########################################
################################################################################


FROZEN_CHOICES = ((True, 'Frozen'),
                  (False, 'Not Frozen'))

ACTIVE_CHOICES = ((True, 'Active'),
                  (False, 'Disabled'))


## Delete Operations

def delete_imagefile(sender,instance,**kwargs):
    if instance.image not in ['',None]:
        if hasattr(instance.image,'datafile'):
            instance.image.datafile.delete()

def delete_remotefile(sender,instance,**kwargs):
    #TODO: need to write this.
    if instance.image not in ['',None]:
        if hasattr(instance.image,'datafile'):
            instance.image.datafile.delete()

verbose_frozen_name="is the container frozen, meaning builds will not be replaced?"


class Container(models.Model):
    '''A local container is a base (singularity) container, stored locally 
       as a file (image) with a unique id and name.
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
                                 verbose_name=verbose_frozen_name)

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
