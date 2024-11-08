from typing import Any

import msgspec

_encoder = msgspec.json.Encoder()


class _MsgspecJsoner:
    def __init__(self, msgspec_type=Any):
        self.encoder = _encoder
        self.decoder = msgspec.json.Decoder(msgspec_type)

    def encode(self, obj, *args, **kwargs):
        return self.encoder.encode(obj)

    def decode(self, obj, *args, **kwargs):
        return self.decoder.decode(obj)


msgspec_jsoner = _MsgspecJsoner()
msgspec_dict_jsoner = _MsgspecJsoner(dict)
msgspec_list_jsoner = _MsgspecJsoner(list)


class MsgspecJsoner:
    def __new__(cls, *args, **kwargs):  # noqa
        return msgspec_jsoner


class MsgspecDictJsoner:
    def __new__(cls, *args, **kwargs):  # noqa
        return msgspec_dict_jsoner


class MsgspecListJsoner:
    def __new__(cls, *args, **kwargs):  # noqa
        return msgspec_list_jsoner
