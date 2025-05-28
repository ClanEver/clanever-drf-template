import logging

import structlog

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt='%Y-%m-%d %H:%M:%S %f', utc=False),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)


def gen_log_setting(log_path, log_level, debug, backup_days: int):
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'plain_console': {
                '()': structlog.stdlib.ProcessorFormatter,
                'processor': structlog.dev.ConsoleRenderer(sort_keys=False),
            },
            'console_to_file': {
                '()': structlog.stdlib.ProcessorFormatter,
                'processor': structlog.dev.ConsoleRenderer(sort_keys=False, colors=False),
            },
            'simple': {
                'format': '%(asctime)s [%(levelname)s] %(name)s %(message)s',
            },
            'db_simple': {
                'format': '%(asctime)s [%(levelname)s] %(name)s\n%(message)s',
            },
        },
        'filters': {},
        'handlers': {
            'console': {
                'level': log_level,
                'class': 'logging.StreamHandler',
                'formatter': 'plain_console',
            },
            'django_file': {
                'level': log_level,
                'formatter': 'simple',
                'class': 'utils.log.SharedThreadedTimeRotatingHandler',
                'file_name': log_path / 'django.log',
                'backup_count': backup_days,
                'when': 'day',
            },
            'db_file': {
                'level': log_level,
                'formatter': 'db_simple',
                'class': 'utils.log.SharedThreadedTimeRotatingHandler',
                'file_name': log_path / 'db.log',
                'backup_count': backup_days,
                'when': 'day',
            },
            'request_file': {
                'level': log_level,
                'formatter': 'console_to_file',
                'class': 'utils.log.SharedThreadedTimeRotatingHandler',
                'file_name': log_path / 'api.log',
                'backup_count': backup_days,
                'when': 'day',
            },
            'error_file': {
                'level': logging.ERROR,
                'formatter': 'console_to_file',
                'class': 'utils.log.SharedThreadedTimeRotatingHandler',
                'file_name': log_path / 'error.log',
                'backup_count': backup_days,
                'when': 'day',
            },
            'no_output': {
                'level': log_level,
                'class': 'logging.NullHandler',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['django_file', 'error_file'],
                'level': max(log_level, logging.INFO),
            },
            'django.request': {
                'handlers': ['no_output'],
                'level': log_level,
                'propagate': False,
            },
            'django.server': {
                'handlers': ['no_output'],
                'level': log_level,
                'propagate': False,
            },
            'django.db.backends': {
                'handlers': ['db_file', 'error_file'],
                'level': log_level,
                'propagate': False,
            },
            'django_structlog': {
                'handlers': ['console', 'request_file', 'error_file'] if debug else ['request_file', 'error_file'],
                'level': log_level,
            },
            'utils.midware': {
                'handlers': ['console', 'request_file', 'error_file'] if debug else ['request_file', 'error_file'],
                'level': log_level,
                'propagate': False,
            },
        },
    }
