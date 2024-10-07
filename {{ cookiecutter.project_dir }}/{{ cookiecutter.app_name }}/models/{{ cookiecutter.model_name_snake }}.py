from django.core import validators
from django.db import models
from import_export import resources

from utils.db import BaseModel


class {{ cookiecutter.model_name }}(BaseModel):

    class Meta:
        verbose_name = '{{ cookiecutter.model_name }}'
        verbose_name_plural = verbose_name


class {{ cookiecutter.model_name }}Resource(resources.ModelResource):
    class Meta:
        model = {{ cookiecutter.model_name }}
        exclude = ('create_time', 'update_time')
