from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from auth_app.models import User
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404


class UserBase(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=30)
    email = serializers.EmailField(required=False)


class RegisterSerializer(UserBase):
    def save(self, **kwargs):
        self.is_valid(raise_exception=True)
        return super().save(**kwargs)

    def create(self, validated_data):
        print(validated_data)
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.clean()
        validate_password(password)
        user.set_password(password)
        user.save()
        return user
