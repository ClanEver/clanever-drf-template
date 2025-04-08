from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView
from rest_framework.routers import SimpleRouter

from admin_patch.admin import dev_tools as admin_dev_tools
from admin_patch.views import dev_tools as view_dev_tools
from admin_patch.views.flower import FlowerProxyView
from admin_patch.views.oidc import OidcViewSet, LogoutViewSet

router = SimpleRouter()
router.register('', OidcViewSet, basename='oidc')
router.register('', LogoutViewSet, basename='logout')

urlpatterns = [
    path('api/o/', include(router.urls)),
    # --- flower ---
    FlowerProxyView.as_url(),
    path(
        'admin/',
        include(
            [
                # --- swagger ---
                path(
                    'schema/',
                    include(
                        [
                            path('', SpectacularAPIView.as_view(), name='schema'),
                            path('swagger-ui/', view_dev_tools.SwaggerView.as_view(url_name='schema'), name='swagger'),
                            path('redoc/', view_dev_tools.RedocView.as_view(url_name='schema'), name='redoc'),
                            path('scalar/', view_dev_tools.scalar, name='scalar'),
                        ]
                    ),
                ),
                # --- admin iframe wrapper ---
                path(
                    'dev_tools/',
                    include(
                        [
                            path('swagger/', admin_dev_tools.SwaggerAdminPage.as_view(), name='dev_tools_swagger'),
                            path('redoc/', admin_dev_tools.RedocAdminPage.as_view(), name='dev_tools_redoc'),
                            path('scalar/', admin_dev_tools.ScalarAdminPage.as_view(), name='dev_tools_scalar'),
                            path('flower/', admin_dev_tools.FlowerAdminPage.as_view(), name='dev_tools_flower'),
                        ]
                    ),
                ),
                # ---django admin ---
                path('', admin.site.urls, name='admin'),
            ]
        ),
    ),
]
