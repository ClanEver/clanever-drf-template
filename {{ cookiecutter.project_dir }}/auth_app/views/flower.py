from django.urls import re_path
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from revproxy.views import ProxyView


class FlowerProxyView(UserPassesTestMixin, ProxyView):
    upstream = settings.FLOWER_URL
    url_prefix = 'flower'
    rewrite: tuple[tuple[str, str]] = ((rf'^/{url_prefix}$', rf'/{url_prefix}/'),)

    def test_func(self):
        return self.request.user.is_superuser

    @classmethod
    def as_url(cls):
        return re_path(rf'^(?P<path>{cls.url_prefix}.*)$', cls.as_view())
