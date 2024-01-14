from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

router = routers.DefaultRouter()

# router.register('example', ExampleViewSet, basename="example")


urlpatterns = [
    # path('', include(router.urls)),
    # path('example/', ExampleViewAPI.as_view(), name='example'),
    path('token/', obtain_auth_token, name='token'),
]
