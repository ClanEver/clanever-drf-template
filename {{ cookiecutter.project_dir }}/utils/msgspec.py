import msgspec

_encoder = msgspec.json.Encoder()
_decoder = msgspec.json.Decoder()


class _MsgspecJsonWrapper:
    @staticmethod
    def encode(obj, *args, **kwargs):
        return _encoder.encode(obj)

    @staticmethod
    def decode(obj, *args, **kwargs):
        return _decoder.decode(obj)


msgspec_json = _MsgspecJsonWrapper()


class MsgspecJsonWrapper:
    def __new__(cls, *args, **kwargs):
        return msgspec_json
