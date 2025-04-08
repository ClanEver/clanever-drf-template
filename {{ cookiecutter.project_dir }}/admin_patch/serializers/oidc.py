from rest_framework import serializers

from admin_patch.models import OidcProvider


class OidcProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = OidcProvider
        fields = ['name', 'icon_url', 'icon_name']


class OidcLoginSerializer(serializers.Serializer):
    url = serializers.CharField()

class OidcCallbackSerializer(serializers.Serializer):
    token = serializers.CharField()
