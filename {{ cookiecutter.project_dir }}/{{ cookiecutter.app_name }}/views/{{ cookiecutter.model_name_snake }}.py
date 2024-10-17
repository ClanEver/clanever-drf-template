from rest_framework import viewsets

from {{ cookiecutter.app_name }}.models import {{ cookiecutter.model_name }}
from {{ cookiecutter.app_name }}.serializers.{{ cookiecutter.model_name_snake }} import {{ cookiecutter.model_name }}Serializer


class {{ cookiecutter.model_name }}ViewSet(viewsets.ModelViewSet):
    queryset = {{ cookiecutter.model_name }}.objects.all()
    serializer_class = {{ cookiecutter.model_name }}Serializer
