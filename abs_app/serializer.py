from re import search
from .models import Version, Application, User
from rest_framework import serializers


class VersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Version
        fields = '__all__'

class ApplicationSerializer(serializers.ModelSerializer):
    available_versions = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = ['id', 'name', 'slug', 'teams_url', 'token', 'available_versions']

    def get_available_versions(self, obj):
        versions = obj.version_set.all()
        serializer = VersionSerializer(versions, many=True)
        return serializer.data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password',
                  'is_admin', 'is_qa', 'is_developer']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)

        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
