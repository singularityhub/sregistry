'''

Copyright (C) 2017-2018 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017-2018 Vanessa Sochat.

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

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from drf_chunked_upload.models import ChunkedUpload as Upload
from djcelery.models import TaskMeta
from six import iteritems


##############################################################################
# Serializer Fields
##############################################################################


class FriendlyChoiceField(serializers.ChoiceField):
    '''Serializer ChoiceField that uses the string representation
    of the choices rather then the int values. Supports creation
    with either choice string or via choice int. It's friendlier.'''
    def __init__(self, choices, **kwargs):
        self.choice_dict = dict(choices)
        kwargs['choices'] = choices
        super(FriendlyChoiceField, self).__init__(**kwargs)

    def to_representation(self, obj):
        # uppercase is more authoritative
        return self.choice_dict[obj].upper()

    def to_internal_value(self, data):
        try:
            # first let's see if we can match to a key
            return self.choice_dict[data]
        except KeyError:
            # if that fails, then let's try to match a value
            # note that this will match the first entry
            # if there multiple keys with the same value
            for key, val in iteritems(self.choice_dict):
                if data.upper() == val.upper():
                    return key
            # if nothing matched then we need to fail
            self.fail('invalid_choice', input=data)


##############################################################################
# Hyperlink Serializers
##############################################################################

class HyperlinkedImageURL(serializers.CharField):
    def to_representation(self, value):
        if value:
            request = self.context.get('request', None)
            return request.build_absolute_uri(value)


class SerializedContributors(serializers.CharField):
    def to_representation(self, value):
        if value:
            return ', '.join([v.username for v in value.all()])


class HyperlinkedDownloadURL(serializers.RelatedField):
    def to_representation(self, value):
        if value:
            print(value)
            print(request)
            request = self.context.get('request', None)
            return request.build_absolute_uri(value + "download")


class HyperlinkedRelatedURL(serializers.RelatedField):
    def to_representation(self, value):
        if value:
            request = self.context.get('request', None)
            return request.build_absolute_uri(value.get_absolute_url())


################################################################################
# Upload Serializers
################################################################################

class TaskSerializer(serializers.ModelSerializer):
    result = serializers.SerializerMethodField()

    def get_result(self, obj):
        if obj.status == 'SUCCESS':
            try:
                pk, content_type = obj.result.split(",")
            except (AttributeError, ValueError):
                pass
            else:
                upload_class = ContentType.model_class(
                    ContentType.objects.get(model=content_type)
                )
                try:
                    return upload_class.objects.get(pk=pk).get_url(
                        self.context['request']
                    )
                except ObjectDoesNotExist:
                    return "object has been deleted"

        return obj.result

    class Meta:
        fields = '__all__'
        model = TaskMeta


class UploadSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="upload-detail")
    user = serializers.HyperlinkedRelatedField(view_name="user-detail",
                                               read_only=True)
    task = TaskSerializer(read_only=True)
    status = FriendlyChoiceField(choices=Upload.STATUS_CHOICES, required=False)

    def validate(self, data):
        model = data['content_type'].model_class()

        if hasattr(model, 'validate'):
            try:
                model.validate(data)
            except ValidationError as e:
                raise serializers.ValidationError(e[0])

        return data

    class Meta:
        model = Upload
        exclude = ('file', )
        read_only_fields = (
            'id', 'status', 'completed_at', 'task', 'offset', 'md5'
        )


class UploadCreateSerializer(UploadSerializer):
    class Meta:
        model = Upload
        fields = '__all__'
        read_only_fields = (
            'id', 'status', 'completed_at', 'task', 'offset', 'md5'
        )
