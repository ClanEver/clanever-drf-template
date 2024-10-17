from django.contrib import admin as django_admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from admin_ext.views.flower import FlowerProxyView
from admin_ext.views.scalar import scalar

urlpatterns = [
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/register/', include('dj_rest_auth.registration.urls')),
    path('admin/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('admin/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),
    path('admin/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('admin/schema/scalar/', scalar, name='scalar'),
    FlowerProxyView.as_url(),
    path('admin/', django_admin.site.urls, name='admin'),
]
