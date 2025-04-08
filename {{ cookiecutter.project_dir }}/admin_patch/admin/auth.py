from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group, Permission
from knox.models import AuthToken
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from admin_patch.models import User
from utils.admin import BaseModelAdmin

admin.site.unregister(Group)
admin.site.unregister(AuthToken)


@admin.register(User)
class UserAdmin(DjangoUserAdmin, BaseModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')
    ordering = ()
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


class PermissionP(Permission):
    class Meta:
        proxy = True
        verbose_name = '权限'
        verbose_name_plural = verbose_name


@admin.register(PermissionP)
class PermissionAdmin(BaseModelAdmin):
    ordering = ('id',)


class GroupP(Group):
    class Meta:
        proxy = True
        verbose_name = '角色'
        verbose_name_plural = verbose_name


@admin.register(GroupP)
class GroupAdmin(BaseModelAdmin):
    pass


@admin.register(AuthToken)
class AuthTokenAdmin(BaseModelAdmin):
    list_display = ('digest_short', 'token_key', 'user', 'created', 'expiry')

    @admin.display(
        description='digest'
    )
    def digest_short(self, obj):
        return obj.digest[:20] + ' ...'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('user').only(
            'digest', 'token_key', 'created', 'expiry', 'user__first_name'
        )
        return qs
