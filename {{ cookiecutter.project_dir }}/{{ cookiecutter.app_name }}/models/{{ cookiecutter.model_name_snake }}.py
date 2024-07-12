from django.core import validators
from django.db import models

from utils.db import BaseModel

class {{ cookiecutter.model_name }}(BaseModel):

    class Meta:
        verbose_name = '{{ cookiecutter.model_name }}'
        verbose_name_plural = verbose_name
