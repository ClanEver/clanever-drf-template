from django.urls import reverse
from rest_framework import serializers

from admin_patch.models import OidcProvider


class OidcProviderSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OidcProvider
        fields = ['name', 'display_name', 'icon_url', 'icon_name', 'url']

    def get_url(self, obj) -> str:
        return reverse('oidc-login', kwargs={'name': obj.name})


class OidcLoginResponseSerializer(serializers.Serializer):
    url = serializers.CharField()


class OidcCallbackSerializer(serializers.Serializer):
    token = serializers.CharField()
