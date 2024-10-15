from django.contrib import admin
from import_export import resources

from {{ cookiecutter.app_name }}.models.{{ cookiecutter.model_name_snake }} import {{ cookiecutter.model_name }}
from utils.admin import BaseModelAdmin


class {{ cookiecutter.model_name }}Resource(resources.ModelResource):
    class Meta:
        model = {{ cookiecutter.model_name }}
        exclude = ('create_time', 'update_time')


@admin.register({{ cookiecutter.model_name }})
class {{ cookiecutter.model_name }}Admin(BaseModelAdmin):
    resource_classes = [{{ cookiecutter.model_name }}Resource]
