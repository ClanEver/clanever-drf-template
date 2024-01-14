from django.db import models


class BaseModel(models.Model):
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    class Meta:
        abstract = True
        verbose_name = 'BaseModel'
        verbose_name_plural = verbose_name
