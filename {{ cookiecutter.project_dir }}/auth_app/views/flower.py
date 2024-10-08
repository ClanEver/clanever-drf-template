from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse
from django.urls import re_path
from revproxy.views import ProxyView


class FlowerProxyView(UserPassesTestMixin, ProxyView):
    upstream = settings.FLOWER_URL
    url_prefix = 'flower'
    rewrite: tuple[tuple[str, str]] = ((rf'^/{url_prefix}$', rf'/{url_prefix}/'),)

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return HttpResponse('403 Permission Denied', status=403)
        return HttpResponse('401 Unauthorized', status=401)

    @classmethod
    def as_url(cls):
        return re_path(rf'^(?P<path>{cls.url_prefix}.*)$', cls.as_view())
