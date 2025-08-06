"""
URL configuration for {{ cookiecutter.project_slug }} project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/zh-hans/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.urls import include, path

urlpatterns = [
    path('api/{{ cookiecutter.app_name }}/', include('{{ cookiecutter.app_name }}.urls'), name='{{ cookiecutter.app_name }}'),
    path('', include('admin_patch.urls'), name='admin'),
]

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls
    from django.conf.urls.static import static

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += debug_toolbar_urls()
