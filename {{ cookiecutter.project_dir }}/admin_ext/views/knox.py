from allauth.account import app_settings as allauth_settings
from allauth.account.utils import complete_signup
from dj_rest_auth.app_settings import api_settings as dj_rest_auth_settings
from dj_rest_auth.models import get_token_model
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView
from django.db import transaction
from django.utils import timezone
from knox.settings import knox_settings
from rest_framework.response import Response

from admin_ext.models import AuthToken
from admin_ext.serializers.knox import KnoxSerializer


class KnoxLoginView(LoginView):
    def check_token_limit_per_user(self):
        token_limit_per_user = knox_settings.TOKEN_LIMIT_PER_USER
        if token_limit_per_user is not None:
            now = timezone.now()
            (
                self.user.auth_token_set.filter(
                    pk__in=self.user.auth_token_set.filter(expiry__gt=now)
                    .order_by('-expiry')
                    .values('pk')[token_limit_per_user:],
                ).delete()
            )

    @transaction.atomic
    def get_response(self):
        self.check_token_limit_per_user()
        serializer_class = self.get_response_serializer()
        data = {
            'user': self.user,
            'token': self.token,
        }
        serializer = serializer_class(instance=data, context={'request': self.request})
        return Response(serializer.data, status=200)


class KnoxRegisterView(RegisterView):
    token: tuple[AuthToken, str]

    def get_response_data(self, user):
        return KnoxSerializer({'user': user, 'token': self.token}).data

    @transaction.atomic
    def perform_create(self, serializer):
        user = serializer.save(self.request)
        token_model = get_token_model()
        self.token = dj_rest_auth_settings.TOKEN_CREATOR(token_model, user, None)
        complete_signup(self.request._request, user, allauth_settings.EMAIL_VERIFICATION, None)
        return user
