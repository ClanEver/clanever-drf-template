import datetime
import uuid
from decimal import Decimal
from typing import Any

import arrow
import msgspec
from django.conf import settings
from django.utils.functional import Promise
from rest_framework.exceptions import ParseError
from rest_framework.parsers import BaseParser
from rest_framework.renderers import BaseRenderer
from rest_framework.settings import api_settings

__all__ = ['MsgspecJSONParser', 'MsgspecJSONRenderer']


class MsgspecJSONParser(BaseParser):
    media_type = 'application/json'

    def parse(self, stream, media_type=None, parser_context=None):  # noqa
        parser_context = parser_context or {}
        encoding = parser_context.get('encoding', settings.DEFAULT_CHARSET)

        try:
            data = stream.read().decode(encoding)
            return msgspec.json.decode(data)
        except msgspec.DecodeError as exc:
            raise ParseError(f'JSON parse error - {exc}') from exc


class JsonRenderError(TypeError):
    pass


def enc_hook(obj: Any) -> Any:  # noqa: PLR0911
    if isinstance(obj, str | uuid.UUID | Promise):
        return str(obj)
    if isinstance(obj, dict):
        return dict(obj)
    if isinstance(obj, list):
        return list(obj)
    if isinstance(obj, datetime.datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(obj, datetime.date):
        return obj.strftime('%Y-%m-%d')
    if isinstance(obj, arrow.Arrow):
        return obj.format('YYYY-MM-DD HH:mm:ss')
    if isinstance(obj, Decimal):
        return str(obj) if api_settings.COERCE_DECIMAL_TO_STRING else float(obj)
    if hasattr(obj, 'tolist'):
        return obj.tolist()
    if hasattr(obj, '__iter__'):
        return list(obj)
    raise JsonRenderError(f'Unknown type: {type(obj)}')


class MsgspecJSONRenderer(BaseRenderer):
    media_type = 'application/json'
    format = 'json'
    ensure_ascii = True
    charset = None

    def render(self, data: Any, *args, **kwargs):  # noqa: ARG002
        if data is None:
            return b''

        encoder = msgspec.json.Encoder(enc_hook=enc_hook)
        return encoder.encode(data)
