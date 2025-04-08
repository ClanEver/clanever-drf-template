from django.contrib import admin
from django.utils.safestring import mark_safe

from admin_patch.models import OidcProvider, OidcUser
from utils.admin import BaseModelAdmin


@admin.register(OidcProvider)
class OidcProviderAdmin(BaseModelAdmin):
    list_display = ('id', 'name', 'icon_pic', 'icon', 'cache_expire_length', 'create_time', 'update_time')
    actions = ['delete_cache']

    @admin.display
    def icon_pic(self, obj: OidcProvider):
        return mark_safe(f'<img src="{obj.icon_url}" width="24" height="24" />') if obj.icon_url else None

    @admin.display
    def icon(self, obj: OidcProvider):
        return mark_safe(
            '<span class="material-symbols-outlined" style="font-size: 24px; vertical-align: middle;">'
            f'{obj.icon_name}</span>'
        )

    @admin.action(description="删除对象缓存")
    def delete_cache(self, request, queryset):
        from admin_patch.views.oidc import OidcViewSet
        for i in queryset.only('name').iterator():
            OidcViewSet.delete_oidc_provider_cache(i.name)


@admin.register(OidcUser)
class OidcUserAdmin(BaseModelAdmin):
    list_display = ('id', 'sub', 'provider', 'user', 'last_login')
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('provider', 'user').only(
            'sub',
            'last_login',
            'provider__name',
            'user__first_name',
        )
        return qs
