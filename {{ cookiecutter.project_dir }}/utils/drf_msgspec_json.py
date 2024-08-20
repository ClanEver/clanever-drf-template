import uuid
from decimal import Decimal
from typing import Any

import msgspec
from django.conf import settings
from django.utils.functional import Promise
from rest_framework.exceptions import ParseError
from rest_framework.parsers import BaseParser
from rest_framework.renderers import BaseRenderer
from rest_framework.settings import api_settings

__all__ = ['MsgspecJSONParser', 'MsgspecJSONRenderer', ]


class MsgspecJSONParser(BaseParser):
    media_type = 'application/json'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Parses the incoming bytestream as JSON and returns the resulting data.
        """
        parser_context = parser_context or {}
        encoding = parser_context.get('encoding', settings.DEFAULT_CHARSET)

        try:
            data = stream.read().decode(encoding)
            return msgspec.json.decode(data)
        except msgspec.DecodeError as exc:
            raise ParseError(f'JSON parse error - {exc}')


def enc_hook(obj: Any) -> Any:
    if isinstance(obj, dict):
        return dict(obj)
    elif isinstance(obj, list):
        return list(obj)
    elif isinstance(obj, Decimal):
        if api_settings.COERCE_DECIMAL_TO_STRING:
            return str(obj)
        else:
            return float(obj)
    elif isinstance(obj, (str, uuid.UUID, Promise)):
        return str(obj)
    elif hasattr(obj, "tolist"):
        return obj.tolist()
    elif hasattr(obj, "__iter__"):
        return list(item for item in obj)


class MsgspecJSONRenderer(BaseRenderer):
    media_type = 'application/json'
    format = 'json'
    ensure_ascii = True
    charset = None

    def render(self, data: Any, *args, **kwargs):
        if data is None:
            return bytes()

        encoder = msgspec.json.Encoder(enc_hook=enc_hook)
        return encoder.encode(data)
