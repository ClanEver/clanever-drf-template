from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def exception_handler(exc, context):
    if settings.DEBUG:
        raise exc
    response = drf_exception_handler(exc, context)
    if not isinstance(response, Response):
        return response

    match response.data:
        case list():
            response.data = {'detail': response.data}
        case dict() if 'detail' not in response.data:
            response.data = {'detail': response.data}
        case _:
            pass
    return response
