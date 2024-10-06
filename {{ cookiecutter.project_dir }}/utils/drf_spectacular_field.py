from drf_spectacular.extensions import OpenApiSerializerFieldExtension


class JsonFieldFix(OpenApiSerializerFieldExtension):
    target_class = 'rest_framework.serializers.JSONField'

    def map_serializer_field(self, auto_schema, direction):  # noqa: ARG002
        return {'type': 'any', 'default': 'json field'}
