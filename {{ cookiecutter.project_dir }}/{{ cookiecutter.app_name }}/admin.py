from django.contrib import admin

from {{ cookiecutter.app_name }}.models.{{ cookiecutter.model_name_snake }} import (
    {{ cookiecutter.model_name }},
    {{ cookiecutter.model_name }}Resource
)
from import_export.admin import ImportExportModelAdmin


@admin.register({{ cookiecutter.model_name }})
class {{ cookiecutter.model_name }}Admin(ImportExportModelAdmin):
    list_display = ("__str__", )
    resource_classes = [{{ cookiecutter.model_name }}Resource]