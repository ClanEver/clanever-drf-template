import structlog
from django.conf import settings
from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin
from rest_framework.response import Response

from utils.drf_msgspec_json import MsgspecJSONRenderer

LOGGER = structlog.stdlib.get_logger(__name__)
SENSITIVE_FIELDS = ['password', 'token']


def sanitize_post_data(post_data):
    # 遮盖敏感信息
    sanitized = dict(post_data)
    for field in SENSITIVE_FIELDS:
        if field in sanitized:
            sanitized[field] = '******'
    return sanitized


def convert_request(request: HttpRequest):
    return {
        # 'status_code': response.status_code,
        'request': f'{request.method} {request.path}',
        'query_params': dict(request.GET),
        'post_data': sanitize_post_data(request.POST),
        # "headers": {k: v for k, v in request.headers.items()},
        'user_name': request.user.username if request.user.is_authenticated else None,
        'content_type': request.content_type,
        'session_id': request.session.session_key,
    }


class Log5xxErrorMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):  # noqa
        log_data = convert_request(request)
        LOGGER.error('unknown_error_print_request', **log_data)


class LogAPIExceptionMiddleware(MiddlewareMixin):
    def process_response(self, request, response):  # noqa
        if response.status_code >= 400 and isinstance(response, Response):
            log_data = convert_request(request)
            detail = (
                response.data.get('detail')
                if isinstance(response, Response) and isinstance(response.data, dict)
                else response.data
            )
            LOGGER.error(
                'api_exception_print_request',
                code=response.status_code,
                detail=detail,
                **log_data,
            )
        return response


class Wrap5xxErrorMiddleware(MiddlewareMixin):
    def process_response(self, request, response):  # noqa
        if not settings.DEBUG and response.status_code >= 500 and not isinstance(response, Response):
            error_response = Response({'detail': 'Internal Server Error'}, status=response.status_code)
            error_response.accepted_renderer = MsgspecJSONRenderer()
            error_response.accepted_media_type = 'application/json'
            error_response.renderer_context = {}
            return error_response.render()
        return response
