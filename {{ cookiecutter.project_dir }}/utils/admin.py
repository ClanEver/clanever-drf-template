from collections.abc import Sequence
from functools import cache
from typing import Any

from django.contrib import admin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import models
from django.views.generic import TemplateView
from import_export.admin import ImportExportMixin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.contrib.import_export.forms import ImportForm, SelectableFieldsExportForm
from unfold.exceptions import UnfoldException


@cache
def _get_admin_list_display(model_class):
    return tuple(
        field.name
        for field in model_class._meta.concrete_fields
        if field.name not in ['create_time', 'update_time']
    ) + tuple(
        field.name for field in model_class._meta.concrete_fields if
        field.name in ['create_time', 'update_time']
    )


class AutoDisplayListMixin:
    model: models.Model
    list_display: Sequence[str]

    def get_list_display(self, request):
        if self.list_display == UnfoldModelAdmin.list_display:
            return _get_admin_list_display(self.model)
        return self.list_display


class BaseModelAdmin(AutoDisplayListMixin, ImportExportMixin, UnfoldModelAdmin):
    import_form_class = ImportForm
    export_form_class = SelectableFieldsExportForm


class CustomIframeAdminPage(PermissionRequiredMixin, TemplateView):
    title: str
    iframe_uri: str
    template_name = 'admin/iframe_base.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        if not hasattr(self, 'title'):
            raise UnfoldException("UnfoldModelAdminViewMixin was not provided with 'title' attribute")

        return super().get_context_data(
            iframe_uri=self.iframe_uri,
            title=self.title,
            **kwargs,
            **admin.site.each_context(self.request),
        )


class IsSuperUserMixIn:
    def has_permission(self):
        return getattr(self.request.user, 'is_superuser', False)
