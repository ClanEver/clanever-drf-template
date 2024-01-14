from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.permissions import IsAuthenticated, AllowAny

from auth_app.serializers.auth import RegisterSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        user = serializer.save()
        return Response(
            {
                "id": user.username
            },
            status=HTTP_200_OK
        )


class LoginView(ObtainAuthToken):
    permission_classes = [AllowAny]
