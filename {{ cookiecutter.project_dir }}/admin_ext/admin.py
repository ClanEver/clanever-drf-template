from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from admin_ext.models import User, AuthToken
from knox.admin import AuthTokenAdmin as KnoxAuthTokenAdmin


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')
    ordering = ()


@admin.register(AuthToken)
class AuthTokenAdmin(KnoxAuthTokenAdmin):
    pass
