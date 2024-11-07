import json
from collections.abc import Callable, Sequence
from functools import lru_cache, partial

from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields.utils import AttributeSetter
from django.core.exceptions import ValidationError
from django.db import models
from django.db.backends.postgresql import operations as django_pgsql_operations
from rest_framework import serializers

from utils.msgspec import MsgspecDictJsoner, MsgspecJsoner, msgspec_jsoner, msgspec_list_jsoner


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

    @classmethod
    def get_list_by_ids(cls, ids: Sequence[int]):
        if not ids:
            return ()
        qs = cls.objects.filter(id=ids[0])
        qs = qs.union(*(cls.objects.filter(id=id_) for id_ in ids[1:]), all=True)
        if len(qs) != len(ids):
            raise cls.DoesNotExist(f'id {",".join(str(x) for x in sorted(set(ids) - {x.id for x in qs}))} 不存在')
        return tuple(qs)


def CONDITIONAL_PROTECT(protect_on: Callable[[models.Model], bool]):  # noqa
    """
    条件保护，任何一个对象满足 protect_on 则保护
    """

    def on_delete(collector, field, sub_objs, using):
        if any(protect_on(x) for x in sub_objs):
            return models.PROTECT(collector, field, sub_objs, using)
        return models.CASCADE(collector, field, sub_objs, using)

    return on_delete


class NoBulkQuerySet(models.QuerySet):
    def bulk_create(self, objs, *args, **kwargs):
        raise models.ProtectedError('不允许 bulk_create', objs)

    def bulk_update(self, objs, *args, **kwargs):
        raise models.ProtectedError('不允许 bulk_update', objs)


class MsgspecJsonField(models.JSONField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('encoder', MsgspecJsoner)
        kwargs.setdefault('decoder', MsgspecJsoner)
        super().__init__(*args, **kwargs)


class DictField(MsgspecJsonField):
    def __init__(self, *args, default=dict, **kwargs):
        kwargs.setdefault('encoder', MsgspecDictJsoner)
        kwargs.setdefault('decoder', MsgspecDictJsoner)
        super().__init__(*args, default=default, **kwargs)

    def validate(self, value, model_instance):
        if not isinstance(value, dict):
            raise ValidationError(f'Value 必须为 dict: {value}')
        super().validate(value, model_instance)


class MsgspecArrayField(ArrayField):
    def __init__(self, base_field, *args, **kwargs):
        kwargs.setdefault('default', list)
        super().__init__(base_field, *args, **kwargs)

    def to_python(self, value):
        if isinstance(value, str):
            vals = msgspec_list_jsoner.decode(value)
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
        return msgspec_list_jsoner.encode(values).decode()


serializers.ModelSerializer.serializer_field_mapping[MsgspecJsonField] = serializers.JSONField
serializers.ModelSerializer.serializer_field_mapping[DictField] = serializers.DictField
serializers.ModelSerializer.serializer_field_mapping[MsgspecArrayField] = serializers.ListField


@lru_cache
def get_json_dumps(encoder):
    if encoder is None:
        return msgspec_jsoner.encode
    return partial(json.dumps, cls=encoder)


django_pgsql_operations.get_json_dumps = get_json_dumps
