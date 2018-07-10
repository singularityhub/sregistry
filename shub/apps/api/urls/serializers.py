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

from rest_framework import serializers

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
