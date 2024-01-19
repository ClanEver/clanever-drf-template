from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from auth_app.views.auth import RegisterView, LoginView

router = routers.DefaultRouter()

# router.register('example', ExampleViewSet, basename="example")


urlpatterns = [
    # path('', include(router.urls)),
    # path('example/', ExampleViewAPI.as_view(), name='example'),
    path('', include('dj_rest_auth.urls')),
    path('register/', include('dj_rest_auth.registration.urls')),
]
