from django.utils.translation import gettext_lazy as _
from drf_spectacular.extensions import OpenApiSerializerFieldExtension


class JsonFieldFix(OpenApiSerializerFieldExtension):
    target_class = 'rest_framework.serializers.JSONField'

    def map_serializer_field(self, auto_schema, direction):  # noqa: ARG002
        return {'type': 'any', 'default': 'json field'}


def postprocess_default_error_response(result, generator, **kwargs):  # noqa: ARG001
    """给所有接口添加默认的 400 和 500 错误响应"""
    if 'Http400Response' not in result['components']['schemas']:
        result['components']['schemas']['Http400Response'] = {
            'properties': {
                'detail': {
                    'example': _('Bad Request'),
                    'oneOf': [{'type': 'string'}, {'type': 'array'}, {'type': 'object'}],
                },
            },
            'required': ['detail'],
            'type': 'object',
        }
        result['components']['schemas']['Http500Response'] = {
            'properties': {
                'detail': {'example': _('A server error occurred.'), 'type': 'string'},
            },
            'required': ['detail'],
            'type': 'object',
        }

    for path in result['paths'].values():
        for method in path.values():
            if '400' not in method['responses']:
                method['responses']['400'] = {
                    'content': {'application/json': {'schema': {'$ref': '#/components/schemas/Http400Response'}}},
                    'description': '',
                }
        for method in path.values():
            if '500' not in method['responses']:
                method['responses']['500'] = {
                    'content': {'application/json': {'schema': {'$ref': '#/components/schemas/Http500Response'}}},
                    'description': '',
                }

    return result
