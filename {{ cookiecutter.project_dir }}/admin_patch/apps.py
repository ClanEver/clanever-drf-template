from django.apps import AppConfig


class AdminPatchConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_patch'
    verbose_name = 'Admin'
    verbose_name_plural = verbose_name
