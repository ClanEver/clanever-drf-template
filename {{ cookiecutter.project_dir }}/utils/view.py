from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def exception_handler(exc, context):
    """
    如果是 DRF 的 Response
    则将错误内容提取到 detail 字段
    """
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
