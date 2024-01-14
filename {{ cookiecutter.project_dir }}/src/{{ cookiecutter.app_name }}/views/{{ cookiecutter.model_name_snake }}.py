from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.permissions import IsAuthenticated, AllowAny

from {{ cookiecutter.app_name }}.models import {{ cookiecutter.model_name }}
from {{ cookiecutter.app_name }}.serializers.{{ cookiecutter.model_name_snake }} import {{ cookiecutter.model_name }}Serializer


class {{ cookiecutter.model_name }}ViewSet(ModelViewSet):
    queryset = {{ cookiecutter.model_name }}.objects.all()
    serializer_class = {{ cookiecutter.model_name }}Serializer
