from django.urls import reverse_lazy

from utils.admin import CustomIframeAdminPage, IsSuperUserMixIn


class SwaggerAdminPage(IsSuperUserMixIn, CustomIframeAdminPage):
    title = 'Swagger'
    iframe_uri = reverse_lazy('swagger')


class RedocAdminPage(IsSuperUserMixIn, CustomIframeAdminPage):
    title = 'Redoc'
    iframe_uri = reverse_lazy('redoc')


class ScalarAdminPage(IsSuperUserMixIn, CustomIframeAdminPage):
    title = 'Scalar'
    iframe_uri = reverse_lazy('scalar')


class FlowerAdminPage(IsSuperUserMixIn, CustomIframeAdminPage):
    title = 'Flower'
    iframe_uri = '/admin/flower/'
