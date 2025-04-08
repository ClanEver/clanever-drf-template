import contextlib

import urllib3
from django.conf import settings
from django.http import HttpResponse
from django.urls import re_path
from django.views.decorators.clickjacking import xframe_options_sameorigin
from revproxy.views import ProxyView

from utils.permission import user_is_superuser


class FlowerProxyView(ProxyView):
    upstream = settings.FLOWER_URL
    url_prefix = r'admin/flower'
    rewrite: tuple[tuple[str, str]] = ((rf'^/{url_prefix}$', rf'/{url_prefix}/'),)

    @classmethod
    def as_url(cls):
        return re_path(rf'^(?P<path>{cls.url_prefix}.*)$', user_is_superuser(cls.as_view()))

    @xframe_options_sameorigin
    def dispatch(self, request, *args, **kwargs):
        with contextlib.suppress(urllib3.exceptions.HTTPError):
            return super().dispatch(request, *args, **kwargs)
        return HttpResponse(b'503 Service Temporarily Unavailable', status=503)
