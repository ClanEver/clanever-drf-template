from dj_rest_auth.serializers import UserDetailsSerializer
from rest_framework import serializers


class KnoxSerializer(serializers.Serializer):
    """
    Serializer for Knox authentication.
    """

    token = serializers.SerializerMethodField()
    user = UserDetailsSerializer()

    def get_token(self, obj):
        return obj['token'][1]
