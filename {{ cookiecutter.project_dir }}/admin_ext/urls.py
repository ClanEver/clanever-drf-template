from dj_rest_auth.registration.views import ResendEmailVerificationView, VerifyEmailView
from dj_rest_auth.views import (
    LogoutView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
    UserDetailsView,
)
from django.contrib import admin as django_admin
from django.urls import path, re_path
from django.views.generic import TemplateView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from admin_ext.views.flower import FlowerProxyView
from admin_ext.views.knox import KnoxLoginView, KnoxRegisterView
from admin_ext.views.scalar import scalar

urlpatterns = [
    # dj_rest_auth + knox
    path('api/auth/password/reset/', PasswordResetView.as_view(), name='rest_password_reset'),
    path('api/auth/password/reset/confirm/', PasswordResetConfirmView.as_view(), name='rest_password_reset_confirm'),
    path('api/auth/login/', KnoxLoginView.as_view(), name='rest_login'),
    path('api/auth/logout/', LogoutView.as_view(), name='rest_logout'),
    path('api/auth/user/', UserDetailsView.as_view(), name='rest_user_details'),
    path('api/auth/password/change/', PasswordChangeView.as_view(), name='rest_password_change'),
    path('api/auth/register/', KnoxRegisterView.as_view(), name='rest_register'),
    path('api/auth/register/verify-email/', VerifyEmailView.as_view(), name='rest_verify_email'),
    path('api/auth/register/resend-email/', ResendEmailVerificationView.as_view(), name='rest_resend_email'),
    re_path(
        r'^account-confirm-email/(?P<key>[-:\w]+)/$',
        TemplateView.as_view(),
        name='account_confirm_email',
    ),
    path(
        'account-email-verification-sent/',
        TemplateView.as_view(),
        name='account_email_verification_sent',
    ),
    # swagger
    path('admin/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('admin/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),
    path('admin/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('admin/schema/scalar/', scalar, name='scalar'),
    # flower
    FlowerProxyView.as_url(),
    # django admin
    path('admin/', django_admin.site.urls, name='admin'),
]
