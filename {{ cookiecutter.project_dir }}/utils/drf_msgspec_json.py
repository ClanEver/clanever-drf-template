import datetime
import uuid
from decimal import Decimal
from typing import Any

import arrow
import msgspec
from django.conf import settings
from django.utils.functional import Promise
from rest_framework.exceptions import ParseError
from rest_framework.fields import DictField
from rest_framework.parsers import BaseParser
from rest_framework.renderers import JSONRenderer
from rest_framework.settings import api_settings

from utils.msgspec import msgspec_jsoner

__all__ = ['MsgspecJSONParser', 'MsgspecJSONRenderer']


class MsgspecJSONParser(BaseParser):
    media_type = 'application/json'

    def parse(self, stream, media_type=None, parser_context=None):  # noqa
        parser_context = parser_context or {}
        encoding = parser_context.get('encoding', settings.DEFAULT_CHARSET)

        try:
            data = stream.read().decode(encoding)
            return msgspec_jsoner.decode(data)
        except msgspec.DecodeError as exc:
            raise ParseError(f'MsgspecJSONParser 解析失败 - {exc}') from exc


class JsonRenderError(TypeError):
    pass


def enc_hook(obj: Any) -> Any:  # noqa: PLR0911
    match obj:
        case str() | uuid.UUID() | Promise():
            return str(obj)
        case dict():
            return dict(obj)
        case list():
            return list(obj)
        case datetime.datetime():
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        case datetime.date():
            return obj.strftime('%Y-%m-%d')
        case arrow.Arrow():
            return obj.format('YYYY-MM-DD HH:mm:ss')
        case Decimal():
            return str(obj) if api_settings.COERCE_DECIMAL_TO_STRING else float(obj)
        case _ if hasattr(obj, 'tolist'):
            return obj.tolist()
        case _ if hasattr(obj, '__iter__'):
            return list(obj)
        case _:
            raise JsonRenderError(f'utils.drf_msgspec_json.enc_hook: 未知类型: {type(obj)}')


class MsgspecJSONRenderer(JSONRenderer):
    encoder = msgspec.json.Encoder(enc_hook=enc_hook)

    def render(self, data, accepted_media_type=None, renderer_context=None):  # noqa
        if data is None:
            return b''

        renderer_context = renderer_context or {}
        indent = self.get_indent(accepted_media_type, renderer_context)

        result_json = self.encoder.encode(data)
        if indent:
            result_json = msgspec.json.format(result_json, indent=indent)
        return result_json


# DictField monkey patch
__DictField_init = DictField.__init__


def __DictField_init_patched(self, **kwargs):  # noqa
    kwargs.pop('encoder', None)
    kwargs.pop('decoder', None)
    return __DictField_init(self, **kwargs)


DictField.__init__ = __DictField_init_patched
