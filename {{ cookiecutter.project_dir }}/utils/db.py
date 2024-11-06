import json
from functools import lru_cache, partial

from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields.utils import AttributeSetter
from django.core.exceptions import ValidationError
from django.db import models
from django.db.backends.postgresql import operations as django_pgsql_operations
from rest_framework import serializers

from utils.msgspec import MsgspecJsonWrapper, msgspec_json


class BaseModel(models.Model):
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)

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
        raise models.ProtectedError('不允许 bulk_create', objs)

    def bulk_update(self, objs, *args, **kwargs):
        raise models.ProtectedError('不允许 bulk_update', objs)


class MsgspecJsonField(models.JSONField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('encoder', MsgspecJsonWrapper)
        kwargs.setdefault('decoder', MsgspecJsonWrapper)
        super().__init__(*args, **kwargs)


class DictField(MsgspecJsonField):
    def __init__(self, *args, default=dict, **kwargs):
        super().__init__(*args, default=default, **kwargs)

    def validate(self, value, model_instance):
        if not isinstance(value, dict):
            raise ValidationError(f'Value must be a dictionary: {value}')
        super().validate(value, model_instance)


class MsgspecArrayField(ArrayField):
    def __init__(self, base_field, *args, **kwargs):
        kwargs.setdefault('default', list)
        super().__init__(base_field=base_field, *args, **kwargs)

    def to_python(self, value):
        if isinstance(value, str):
            vals = msgspec_json.decode(value)
            value = [self.base_field.to_python(val) for val in vals]
        return value

    def value_to_string(self, obj):
        values = []
        vals = self.value_from_object(obj)
        base_field = self.base_field

        for val in vals:
            if val is None:
                values.append(None)
            else:
                obj = AttributeSetter(base_field.attname, val)
                values.append(base_field.value_to_string(obj))
        return msgspec_json.encode(values).decode()


serializers.ModelSerializer.serializer_field_mapping[MsgspecJsonField] = serializers.JSONField
serializers.ModelSerializer.serializer_field_mapping[DictField] = serializers.DictField
serializers.ModelSerializer.serializer_field_mapping[MsgspecArrayField] = serializers.ListField


@lru_cache
def get_json_dumps(encoder):
    if encoder is None:
        return msgspec_json.encode
    return partial(json.dumps, cls=encoder)


django_pgsql_operations.get_json_dumps = get_json_dumps
