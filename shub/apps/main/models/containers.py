'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from shub.apps.api.models import ImageFile
from django.urls import reverse
from django.db import models
from django.db.models.signals import pre_delete

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


FROZEN_CHOICES = ((True, 'Frozen'),
                  (False, 'Not Frozen'))

ACTIVE_CHOICES = ((True, 'Active'),
                  (False, 'Disabled'))


def delete_imagefile(sender, instance, **kwargs):
    if instance.image not in ['', None]:
        if hasattr(instance.image, 'datafile'):
            instance.image.datafile.delete()

################################################################################
# Containers ###################################################################
################################################################################


verbose_frozen_name = "is the container frozen, meaning builds will not be replaced?"

class Container(models.Model):
    '''A container is a base (singularity) container with a unique id and name
    '''
    add_date = models.DateTimeField('date container added', auto_now=True)

    # When the collection is deleted, DO delete the Container object
    collection = models.ForeignKey('main.Collection', null=False, blank=False, 
                                                      related_name="containers", 
                                                      on_delete=models.CASCADE)

    # When the Image File is deleted, don't delete the Container object (can be updated)
    image = models.ForeignKey(ImageFile, null=True, blank=False, on_delete=models.SET_NULL)
    metadata = JSONField(default=dict, blank=True)
    metrics = JSONField(default=dict, blank=True)
    name = models.CharField(max_length=250, null=False, blank=False)
    tag = models.CharField(max_length=250, null=False, blank=False, default="latest")
    secret = models.CharField(max_length=250, null=True, blank=True)
    version = models.CharField(max_length=250, null=True, blank=True)
    tags = TaggableManager()
    frozen = models.BooleanField(choices=FROZEN_CHOICES,
                                 default=False,
                                 verbose_name=verbose_frozen_name)

    # A helper function to get an image.
    def get_image(self):

        # A remote build will have an image path stored as metadata
        if self.image is None:
            if "image" in self.metadata:
                if self.metadata['image'] is not None:   
                    return self.metadata['image']

        # Otherwise return None (no image) or the file
        return self.image

    # A container only gets a version when it's frozen, otherwise known by tag
    def get_short_uri(self):

        # An automated build means a collection has a common namespace
        if "/" in self.name:
            return "%s:%s" %(self.name, self.tag)
        return "%s/%s:%s" %(self.collection.name,
                            self.name,
                            self.tag)

    def get_uri(self): # shub://username/reponame:branch@tag
        if not self.frozen:
            return self.get_short_uri()

        # An automated build means a collection has a common namespace
        version = "%s@%s" %(self.tag, self.version)
        if "/" in self.name:
            return "%s:%s" %(self.name, version)
        return "%s/%s:%s" %(self.collection.name,
                            self.name,
                            version)

    def update_secret(self, save=True):
        '''secret exists to make brute force download not possible'''
        self.secret = str(uuid.uuid4())
        if save is True:
            self.save()

    def save(self, *args, **kwargs):
        '''update secret on each save'''
        self.update_secret(save=False)
        super(Container, self).save(*args, **kwargs)

    def get_image_path(self):
        if self.image not in [None, ""]:
            return self.image.datafile.path
        return None

    def get_download_name(self, extension="sif"):
        return "%s.%s" %(self.get_uri().replace('/', '-'), extension)

    def members(self):
        return get_collection_users(self)

    def get_download_url(self):
        if self.image not in [None, ""]:
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
        unique_together = (("name", "tag", "collection"),)

    def get_absolute_url(self):
        return_cid = self.id
        return reverse('container_details', args=[str(return_cid)])


    def labels(self):
        from shub.apps.main.models import Label
        return Label.objects.filter(containers=self)
        

    def has_edit_permission(self, request):
        return has_edit_permission(request=request,
                                   instance=self.collection)

    def has_view_permission(self, request):
        return has_view_permission(request=request,
                                   instance=self.collection)



pre_delete.connect(delete_imagefile, sender=Container)
