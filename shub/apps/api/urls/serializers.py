"""

Copyright (C) 2017-2021 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from rest_framework import serializers

################################################################################
# Hyperlink Serializers
################################################################################


class HyperlinkedImageURL(serializers.CharField):
    def to_representation(self, value):
        if value:
            request = self.context.get("request", None)
            return request.build_absolute_uri(value)


class SerializedContributors(serializers.CharField):
    def to_representation(self, value):
        if value:
            return ", ".join([v.username for v in value.all()])


class HyperlinkedDownloadURL(serializers.RelatedField):
    def to_representation(self, value):
        if value:
            request = self.context.get("request", None)
            return request.build_absolute_uri(value + "download")


class HyperlinkedRelatedURL(serializers.RelatedField):
    def to_representation(self, value):
        if value:
            request = self.context.get("request", None)
            return request.build_absolute_uri(value.get_absolute_url())
