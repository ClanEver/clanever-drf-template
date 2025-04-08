from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_sameorigin
from drf_spectacular.settings import spectacular_settings
from drf_spectacular.views import SpectacularRedocView, SpectacularSwaggerView

from utils.permission import user_is_superuser


@user_is_superuser
@xframe_options_sameorigin
def scalar(request):
    context = {'title': spectacular_settings.TITLE}
    return render(request, 'scalar.html', context)


class SwaggerView(SpectacularSwaggerView):
    @xframe_options_sameorigin
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class RedocView(SpectacularRedocView):
    @xframe_options_sameorigin
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
