import time
from urllib.parse import urljoin

import arrow
from authlib.common.security import generate_token
from authlib.jose import JsonWebEncryption, jwt
from django.conf import settings
from django.core.cache import cache
from django.db.transaction import atomic
from django.shortcuts import redirect
from django.urls import reverse
from drf_spectacular.utils import extend_schema
from knox.models import AuthToken
from knox.settings import knox_settings
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from admin_patch.models import OidcProvider, OidcUser, User
from admin_patch.serializers.oidc import OidcCallbackSerializer, OidcLoginSerializer, OidcProviderSerializer
from utils.common import random_str
from utils.exception import APIException


class OidcViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = OidcProvider.objects.all().order_by('id')
    serializer_class = OidcProviderSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    jwe = JsonWebEncryption()

    @staticmethod
    def get_oidc_provider(name: str):
        if not (obj := cache.get(f'oidc_provider:{name}')):
            obj: OidcProvider = get_object_or_404(OidcProvider.objects.all(), name=name)
            _ = obj.well_known
            _ = obj.jwks
            cache.set(f'oidc_provider:{name}', obj, obj.cache_expire_length)
        return obj

    @staticmethod
    def delete_oidc_provider_cache(name: str):
        cache.delete(f'oidc_provider:{name}')

    @staticmethod
    def get_redirect_uri(request: Request, provider: str):
        base_url = f'{request.scheme}://{request.get_host()}'
        callback_path = reverse('oidc-callback', kwargs={'pk': provider})
        return urljoin(base_url, callback_path)

    @staticmethod
    def get_or_create_user(provider: OidcProvider, jwt_dict: dict):
        oidc_info = {
            'sub': jwt_dict['sub'],
            'email': jwt_dict['email'],
            'preferred_username': jwt_dict['preferred_username'],
            'given_name': jwt_dict.get('given_name'),
            'groups': jwt_dict.get('groups'),
            'name': jwt_dict.get('name'),
            'nickname': jwt_dict.get('nickname'),
        }

        sub = oidc_info['sub']
        oidc_user = OidcUser.objects.select_related('user').filter(provider=provider, sub=sub).first()
        if oidc_user:
            oidc_user.oidc_info = oidc_info
            return oidc_user.user, oidc_user

        email = oidc_info['email']
        if User.objects.filter(email=email).exists():
            raise APIException('此邮箱已被注册', status.HTTP_400_BAD_REQUEST)

        username = ori_username = oidc_info['preferred_username']
        while len(username) < 4 or User.objects.filter(username=username).exists():
            username = ori_username + random_str(4, False)

        user = User(
            username=username,
            email=email,
            first_name=oidc_info['nickname'] or oidc_info['name'] or username,
            last_name=oidc_info['given_name'] or '',
        )
        oidc_user = OidcUser(
            provider=provider,
            sub=sub,
            user=user,
            oidc_info=oidc_info,
        )

        return user, oidc_user

    @staticmethod
    def delete_extra_token(user: User):
        """删除多余的 token"""
        if knox_settings.TOKEN_LIMIT_PER_USER:
            user.auth_token_set.filter(
                pk__in=user.auth_token_set
                       .order_by('-expiry')
                       .values('pk')[knox_settings.TOKEN_LIMIT_PER_USER:],
            ).delete()

    @extend_schema(responses=OidcLoginSerializer)
    @action(['GET'], True)
    def login(self, request: Request, *args, **kwargs):
        is_redirect = request.query_params.get("redirect")
        provider = kwargs.get('pk')
        oidc_provider = self.get_oidc_provider(provider)
        nonce = generate_token()
        code_verifier = generate_token()

        try:
            auth_url, csrf_state = oidc_provider.client.create_authorization_url(
                oidc_provider.well_known['authorization_endpoint'],
                nonce=nonce,
                redirect_uri=self.get_redirect_uri(request, provider),
                code_verifier=code_verifier,
            )
        except Exception as e:
            raise APIException() from e
        request.session['oidc_state'] = csrf_state

        cache.set(f'oidc_state:{provider}:{csrf_state}', (nonce, code_verifier), 60)

        if is_redirect == '1':
            return redirect(auth_url)
        else:
            return Response({'url': auth_url})

    @extend_schema(responses={200: OidcCallbackSerializer})
    @action(['GET'], True)
    def callback(self, request: Request, *args, **kwargs):
        provider = kwargs.get('pk')
        oidc_provider = self.get_oidc_provider(provider)
        code = request.GET.get('code')
        state = request.GET.get('state')

        if request.session.get('oidc_state') != state:
            raise APIException('Bad Request', status.HTTP_400_BAD_REQUEST)

        state_cache = cache.get(f'oidc_state:{provider}:{state}')
        if not state_cache:
            raise APIException('Bad Request', status.HTTP_400_BAD_REQUEST)

        nonce, code_verifier = state_cache

        try:
            r = oidc_provider.client.fetch_token(
                oidc_provider.well_known['token_endpoint'],
                code=code,
                state=state,
                grant_type='authorization_code',
                redirect_uri=self.get_redirect_uri(request, provider),
                code_verifier=code_verifier,
            )
        except Exception as e:
            raise APIException('Bad Request', status.HTTP_400_BAD_REQUEST) from e

        access_token = r['access_token']
        if oidc_provider.private_key:
            jwe_dict = self.jwe.deserialize_compact(access_token, oidc_provider.private_key)
            jwt_dict = jwt.decode(jwe_dict['payload'], oidc_provider.key_set)
        else:
            jwt_dict = jwt.decode(access_token, oidc_provider.key_set)

        now = time.time()
        if (
                jwt_dict['nonce'] != nonce
                or jwt_dict['iss'] != oidc_provider.well_known['issuer']
                or jwt_dict['aud'] != oidc_provider.client_id
                or jwt_dict['exp'] < now < jwt_dict['iat']
        ):
            raise APIException('Bad Request', status.HTTP_400_BAD_REQUEST)

        user, oidc_user = self.get_or_create_user(oidc_provider, jwt_dict)
        with atomic():
            oidc_user.last_login = oidc_user.user.last_login = arrow.now(settings.TIME_ZONE).datetime
            user.save()
            oidc_user.save()
            _, token = AuthToken.objects.create(user=oidc_user.user)  # 创建 token

        self.delete_extra_token(user)
        return Response({'token': token})


class LogoutViewSet(viewsets.GenericViewSet):
    @extend_schema(responses={204: None})
    @action(['GET'], False)
    def logout(self, request: Request, *args, **kwargs):
        request.auth.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(responses={204: None})
    @action(['GET'], False)
    def logout_all(self, request: Request, *args, **kwargs):
        request.user.auth_token_set.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
