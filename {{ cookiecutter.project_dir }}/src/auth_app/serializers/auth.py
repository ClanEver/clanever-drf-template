from rest_framework import serializers

from auth_app.models import User
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404


class UserBase:
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=30)
    email = serializers.EmailField(allow_blank=True)


class RegisterSerializer(UserBase, serializers.Serializer):
    def save(self, **kwargs):
        self.is_valid(raise_exception=True)
        data: dict = self.validated_data
        password = data.get('password')
        user = User(**data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(UserBase, serializers.Serializer):
    def save(self, **kwargs):
        self.is_valid(raise_exception=True)
        data: dict = self.validated_data
        username = data.get('username')
        password = data.get('password')
        user = get_object_or_404(User, username=username)
        if not user.check_password(password):
            raise ValidationError('用户名或密码错误')
        token, _ = Token.objects.get_or_create(user=user)
        return token.key
