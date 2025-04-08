from django.contrib import admin
from django_celery_beat.admin import (
    ClockedScheduleAdmin as _ClockedScheduleAdmin,
)
from django_celery_beat.admin import (
    CrontabScheduleAdmin as _CrontabScheduleAdmin,
)
from django_celery_beat.admin import (
    IntervalScheduleAdmin as _IntervalScheduleAdmin,
)
from django_celery_beat.admin import PeriodicTaskAdmin as _PeriodicTaskAdmin
from django_celery_beat.admin import (
    PeriodicTaskForm,
    TaskSelectWidget,
)
from django_celery_beat.admin import SolarScheduleAdmin as _SolarScheduleAdmin
from django_celery_beat.models import (
    ClockedSchedule,
    CrontabSchedule,
    IntervalSchedule,
    PeriodicTask,
    SolarSchedule,
)
from django_celery_results.admin import GroupResultAdmin as _GroupResultAdmin
from django_celery_results.admin import TaskResultAdmin as _TaskResultAdmin
from django_celery_results.models import GroupResult, TaskResult
from unfold.admin import ModelAdmin
from unfold.widgets import UnfoldAdminSelectWidget, UnfoldAdminTextInputWidget

admin.site.unregister(PeriodicTask)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(SolarSchedule)
admin.site.unregister(ClockedSchedule)
admin.site.unregister(TaskResult)
admin.site.unregister(GroupResult)


class UnfoldTaskSelectWidget(UnfoldAdminSelectWidget, TaskSelectWidget):
    pass


class UnfoldPeriodicTaskForm(PeriodicTaskForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['task'].widget = UnfoldAdminTextInputWidget()
        self.fields['regtask'].widget = UnfoldTaskSelectWidget()


class PeriodicTaskP(PeriodicTask):
    class Meta:
        proxy = True
        verbose_name = '任务'
        verbose_name_plural = verbose_name


@admin.register(PeriodicTaskP)
class PeriodicTaskAdmin(_PeriodicTaskAdmin, ModelAdmin):
    form = UnfoldPeriodicTaskForm


class IntervalScheduleP(IntervalSchedule):
    class Meta:
        proxy = True
        verbose_name = '调度器 - 间隔'
        verbose_name_plural = verbose_name


@admin.register(IntervalScheduleP)
class IntervalScheduleAdmin(_IntervalScheduleAdmin, ModelAdmin):
    pass


class CrontabScheduleP(CrontabSchedule):
    class Meta:
        proxy = True
        verbose_name = '调度器 - Crontab'
        verbose_name_plural = verbose_name


@admin.register(CrontabScheduleP)
class CrontabScheduleAdmin(_CrontabScheduleAdmin, ModelAdmin):
    pass


class SolarScheduleP(SolarSchedule):
    class Meta:
        proxy = True
        verbose_name = '调度器 - 天文事件'
        verbose_name_plural = verbose_name


@admin.register(SolarScheduleP)
class SolarScheduleAdmin(_SolarScheduleAdmin, ModelAdmin):
    pass


class ClockedScheduleP(ClockedSchedule):
    class Meta:
        proxy = True
        verbose_name = '调度器 - 定时'
        verbose_name_plural = verbose_name


@admin.register(ClockedScheduleP)
class ClockedScheduleAdmin(_ClockedScheduleAdmin, ModelAdmin):
    pass


class TaskResultP(TaskResult):
    class Meta:
        proxy = True
        verbose_name = '任务结果'
        verbose_name_plural = verbose_name


@admin.register(TaskResultP)
class TaskResultAdmin(_TaskResultAdmin, ModelAdmin):
    pass


class GroupResultP(GroupResult):
    class Meta:
        proxy = True
        verbose_name = '任务组结果'
        verbose_name_plural = verbose_name


@admin.register(GroupResultP)
class GroupResultAdmin(_GroupResultAdmin, ModelAdmin):
    pass
