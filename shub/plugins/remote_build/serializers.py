from rest_framework import serializers


class BuildContainersSerializer(serializers.Serializer):
    buildid = serializers.CharField(max_length=32)

    def create(self, validated_data):
        return BuildContainer.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.buildid = validated_data.get('buildid', instance.buildid)

        instance.save()
        return instance
