import logging
import os

import structlog
from celery import Celery
from celery.signals import setup_logging
from django.conf import settings
from django_structlog.celery.steps import DjangoStructLogInitStep
from utils.log import ClanRichTracebackFormatter, format_exception_to_io

# 为'celery'程序设置默认的Django设置模块。
# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{{ cookiecutter.project_slug }}.settings')

app = Celery('test3')
app.steps['worker'].add(DjangoStructLogInitStep)

# 在这里使用字符串意味着 worker 不需要序列化配置对象到子进程。
# namespace='CELERY' 意味着所有与 celery 相关的配置键应该有一个 'CELERY_' 前缀。
# Using a string here means the worker doesn't have to serialize the configuration object to child processes.
# namespace='CELERY' means all celery-related configuration keys should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# 从所有已注册的 Django 应用中加载任务模块。
# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@setup_logging.connect
def receiver_setup_logging(loglevel, logfile, format, colorize, **kwargs):  # noqa: A002, ARG001
    from {{ cookiecutter.project_slug }} import log_setting

    del log_setting
    logging.config.dictConfig(
        {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'plain_console': {
                    '()': structlog.stdlib.ProcessorFormatter,
                    'processor': structlog.dev.ConsoleRenderer(
                        sort_keys=False,
                        exception_formatter=ClanRichTracebackFormatter(
                            color_system='truecolor',
                            highlight=True,
                        ),
                    ),
                },
                'console_to_file': {
                    '()': structlog.stdlib.ProcessorFormatter,
                    'processor': structlog.dev.ConsoleRenderer(
                        colors=False,
                        exception_formatter=format_exception_to_io,
                    ),
                },
            },
            'handlers': {
                'console': {
                    'level': loglevel,
                    'class': 'logging.StreamHandler',
                    'formatter': 'plain_console',
                },
                'celery_file': {
                    'level': loglevel,
                    'formatter': 'console_to_file',
                    'class': 'utils.log.SharedThreadedTimeRotatingHandler',
                    'file_name': settings.LOG_PATH / 'celery.log',
                    'backup_count': 15,
                    'when': 'day',
                },
                'no_output': {
                    'level': loglevel,
                    'class': 'logging.NullHandler',
                },
            },
            'loggers': {
                'django_structlog.celery.receivers': {
                    'handlers': (
                        ['console', 'celery_file']
                        if settings.DEBUG
                        else ['celery_file']
                    ),
                    'level': loglevel,
                    'propagate': False,
                },
                'celery': {
                    'handlers': ['no_output'],
                    'level': loglevel,
                },
            },
        },
    )


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


@app.task(queue='priority')
def debug_priority_task():
    return 'This is a priority task'
