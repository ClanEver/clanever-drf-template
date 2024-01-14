from django.urls import include, path
from rest_framework import routers

from .views.{{ cookiecutter.model_name_snake }} import {{ cookiecutter.model_name }}ViewSet

router = routers.DefaultRouter()

router.register('{{ cookiecutter.model_name_snake }}', {{ cookiecutter.model_name }}ViewSet, basename="{{ cookiecutter.model_name_snake }}")


urlpatterns = [
    path('', include(router.urls)),
    # path('example/', ExampleViewAPI.as_view(), name='example'),
]
