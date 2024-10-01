import logging

import structlog

from utils.log import ClanRichTracebackFormatter, LogMsgspecJsonRenderer, format_exception_to_io

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt='%Y', utc=False),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        # structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)


def gen_log_setting(log_path, log_level, debug):
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json_formatter': {
                '()': structlog.stdlib.ProcessorFormatter,
                # 'processor': structlog.processors.JSONRenderer(),
                'processor': LogMsgspecJsonRenderer(),
            },
            'plain_console': {
                '()': structlog.stdlib.ProcessorFormatter,
                'processor': structlog.dev.ConsoleRenderer(
                    sort_keys=False,
                    exception_formatter=ClanRichTracebackFormatter(color_system='truecolor', highlight=True),  # type: ignore
                ),
            },
            'django_console_to_file': {
                '()': structlog.stdlib.ProcessorFormatter,
                'format': '%(asctime)s [%(levelname)s] %(message)s',
                'processor': structlog.dev.ConsoleRenderer(
                    colors=False,
                    exception_formatter=format_exception_to_io,  # type: ignore
                ),
            },
            'console_to_file': {
                '()': structlog.stdlib.ProcessorFormatter,
                'processor': structlog.dev.ConsoleRenderer(
                    colors=False,
                    exception_formatter=format_exception_to_io,  # type: ignore
                ),
            },
            'key_value': {
                '()': structlog.stdlib.ProcessorFormatter,
                'processor': structlog.processors.KeyValueRenderer(
                    key_order=['timestamp', 'level', 'event', 'logger'],
                ),
            },
            'simple': {
                'format': '%(asctime)s [%(levelname)s] %(message)s',
            },
        },
        'filters': {},
        'handlers': {
            # 'json_file': {
            #     'level': log_level,
            #     'formatter': 'json_formatter',
            #     'class': 'utils.log.ClanThreadedTimeRotatingHandler',
            #     'file_name': log_path / 'json.log',
            #     'backup_count': 15,
            #     'when': 'day',
            # },
            'django_file': {
                'level': max(log_level, logging.WARNING),
                'formatter': 'console_to_file',
                'class': 'utils.log.ThreadedTimeRotatingHandler',
                'file_name': log_path / 'django.log',
                'backup_count': 15,
                'when': 'day',
            },
            'api_file': {
                'level': log_level,
                'formatter': 'console_to_file',
                'class': 'utils.log.ThreadedTimeRotatingHandler',
                'file_name': log_path / 'api.log',
                'backup_count': 15,
                'when': 'day',
            },
            'db_file': {
                'level': log_level,
                'formatter': 'console_to_file',
                'class': 'utils.log.ThreadedTimeRotatingHandler',
                'file_name': log_path / 'db.log',
                'backup_count': 15,
                'when': 'day',
            },
            'beat_file': {
                'level': log_level,
                'formatter': 'console_to_file',
                'class': 'utils.log.ThreadedTimeRotatingHandler',
                'file_name': log_path / 'beat.log',
                'backup_count': 15,
                'when': 'day',
            },
            'worker_file': {
                'level': log_level,
                'formatter': 'console_to_file',
                'class': 'utils.log.ThreadedTimeRotatingHandler',
                'file_name': log_path / 'worker.log',
                'backup_count': 15,
                'when': 'day',
            },
            'console': {
                'level': log_level,
                'class': 'logging.StreamHandler',
                'formatter': 'plain_console',
            },
            'no_output': {
                'level': log_level,
                'class': 'logging.NullHandler',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['django_file'],
                'level': max(log_level, logging.WARNING),
            },
            'django.db.backends': {
                'handlers': ['db_file'],
                'level': log_level,
            },
            'django_structlog': {
                'handlers': ['console', 'api_file'] if debug else ['api_file'],
                'level': log_level,
            },
            'utils': {
                'handlers': ['console', 'api_file'] if debug else ['api_file'],
                'level': log_level,
            },
            'worker': {
                'handlers': ['console', 'worker_file'] if debug else ['worker_file'],
                'level': log_level,
            },
            'beat': {
                'handlers': ['console', 'beat_file'] if debug else ['beat_file'],
                'level': log_level,
            },
        },
    }
