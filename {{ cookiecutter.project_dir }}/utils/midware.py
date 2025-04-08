import structlog
from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response

from utils.drf_msgspec_json import MsgspecJSONRenderer

LOGGER = structlog.stdlib.get_logger(__name__)
SENSITIVE_FIELDS = {'password', 'token', 'old_password', 'new_password1', 'new_password2', 'Authorization'}


def sanitize_data(post_data):
    """遮盖敏感信息"""
    sanitized = dict(post_data)
    for field in SENSITIVE_FIELDS:
        if field in sanitized:
            sanitized[field] = '*'
    return sanitized


def convert_request(request: HttpRequest):
    return {
        # 'status_code': response.status_code,
        'request': f'{request.method} {request.path}',
        'query_params': dict(request.GET),
        'post_data': sanitize_data(request.POST),
        "headers": sanitize_data(request.headers),
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
        from django.conf import settings

        # 如果是 DEBUG 则不处理非 drf 5xx 异常
        if settings.DEBUG or response.status_code <= 499 or isinstance(response, Response):
            return response

        error_response = Response({'detail': _()}, status=response.status_code)
        error_response.accepted_renderer = MsgspecJSONRenderer()
        error_response.accepted_media_type = 'application/json'
        error_response.renderer_context = {}
        return error_response.render()
