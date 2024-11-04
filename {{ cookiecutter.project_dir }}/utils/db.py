import msgspec
from django.core.exceptions import ValidationError
from django.db import models


class BaseModel(models.Model):
    create_time = models.DateTimeField(verbose_name=_('创建时间'), auto_now_add=True)
    update_time = models.DateTimeField(verbose_name=_('更新时间'), auto_now=True)

    class Meta:
        abstract = True
        verbose_name = 'BaseModel'
        verbose_name_plural = verbose_name

    __repr_exclude__ = {'_state', 'create_time', 'update_time'}

    def __repr__(self):
        return (
            f'<{self.__class__.__name__} '
            f'{" ".join(f"{k}={v}" for k, v in self.__dict__.items() if k not in self.__repr_exclude__)}>'
        )


class NoBulkQuerySet(models.QuerySet):
    def bulk_create(self, objs, *args, **kwargs):
        raise models.ProtectedError('bulk_create is not allowed on this model', objs)

    def bulk_update(self, objs, *args, **kwargs):
        raise models.ProtectedError('bulk_update is not allowed on this model', objs)


class MsgspecJsonField(models.JSONField):
    def __init__(self, *args, msgspec_type=None, **kwargs):
        self.msgspec_type = msgspec_type
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        try:
            return msgspec.json.decode(value, type=self.msgspec_type)
        except msgspec.DecodeError as e:
            raise ValidationError(f'Invalid JSON data: {value}') from e

    def to_python(self, value):
        if isinstance(value, str):
            try:
                return msgspec.json.decode(value, type=self.msgspec_type)
            except msgspec.DecodeError as e:
                raise ValidationError(f'Invalid JSON data: {value}') from e
        return value

    def get_prep_value(self, value):
        if value is None:
            return value
        try:
            return msgspec.json.encode(value).decode('utf-8')
        except msgspec.EncodeError as e:
            raise ValidationError(f'Cannot encode to JSON: {value}') from e

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        try:
            msgspec.json.encode(value)
        except msgspec.EncodeError as e:
            raise ValidationError(f'Invalid data for Msgspec encoding: {value}') from e


class DictField(MsgspecJsonField):
    def __init__(self, *args, msgspec_type=dict, default=dict, **kwargs):
        super().__init__(*args, msgspec_type=msgspec_type, default=default, **kwargs)

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        if not isinstance(value, dict):
            raise ValidationError(f'Value must be a dictionary: {value}')


class ListField(MsgspecJsonField):
    def __init__(self, *args, msgspec_type=list, default=list, **kwargs):
        super().__init__(*args, msgspec_type=msgspec_type, default=default, **kwargs)

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        if not isinstance(value, list):
            raise ValidationError(f'Value must be a list: {value}')
