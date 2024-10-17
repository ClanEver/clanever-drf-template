from django.shortcuts import render
from drf_spectacular.settings import spectacular_settings

from auth_app.permissions import user_is_superuser


@user_is_superuser
def scalar(request):
    context = {'title': spectacular_settings.TITLE}
    return render(request, 'scalar.html', context)
