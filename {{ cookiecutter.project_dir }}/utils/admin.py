from collections.abc import Iterator

from django.contrib import admin
from django.db import models
from import_export.admin import ImportExportMixin


class AutoDisplayListMixin:
    model: models.Model
    list_display: Iterator[str]

    def get_list_display(self, request):
        if self.list_display == admin.ModelAdmin.list_display:
            return tuple(field.name for field in self.model._meta.concrete_fields)
        return self.list_display


class BaseModelAdmin(AutoDisplayListMixin, ImportExportMixin, admin.ModelAdmin):
    pass
