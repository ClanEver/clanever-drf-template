"""
For more information on this file, see
https://docs.djangoproject.com/zh-hans/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/zh-hans/5.1/ref/settings/
"""

import os
from pathlib import Path

import structlog

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------- 自定义设置 ----------------
class __BaseConfig:
    DEBUG = False
    DATABASES: dict = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    LOG_PATH = BASE_DIR / 'logs'


class DevConfig(__BaseConfig):
    DEBUG: bool = True
    DATABASES: dict = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


class TestConfig(__BaseConfig):
    pass


class ProdConfig(__BaseConfig):
    DATABASES: dict = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "mydatabase",
            "USER": "mydatabaseuser",
            "PASSWORD": "mypassword",
            "HOST": "127.0.0.1",
            "PORT": "5432",
            "OPTIONS": {
                # 连接池参数参考 https://www.psycopg.org/psycopg3/docs/api/pool.html#the-connectionpool-class
                "pool": {
                    "min_size": 2,
                    "max_size": 10,
                    "timeout": 10,
                }
            },
        }
    }


DJANGO_CONFIG = os.environ.get('DJANGO_CONFIG', 'dev')
config = {
    'dev': DevConfig,
    'test': TestConfig,
    'prod': ProdConfig,
}.get(DJANGO_CONFIG)


# ---------------- django设置 ----------------
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-!!!SET DJANGO_SECRET_KEY!!!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config.DEBUG

ALLOWED_HOSTS = []


# Application definition
SITE_ID = 1
INSTALLED_APPS = [
    # django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # third-party
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'dj_rest_auth.registration',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'django_celery_results',
    'django_celery_beat',
    # your apps
    'auth_app',
    'my_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = '{{ cookiecutter.project_slug }}.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = '{{ cookiecutter.project_slug }}.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = config.DATABASES


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
] if not DEBUG else []


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = "auth_app.User"


# REST_FRAMEWORK
REST_FRAMEWORK = {
    # authentication
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # pagination
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
    # msgspec
    'DEFAULT_RENDERER_CLASSES': [
        'utils.drf_msgspec_json.MsgspecJSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'utils.drf_msgspec_json.MsgspecJSONParser',
    ],
    # drf-spectacular
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}


# drf-spectacular
SPECTACULAR_SETTINGS = {
    'TITLE': '{{ cookiecutter.project_name }} API',
    'DESCRIPTION': '{{ cookiecutter.description }}',
    'VERSION': '0.1.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_DIST': 'SIDECAR',
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
    # OTHER SETTINGS
}


# email config -> https://docs.djangoproject.com/zh-hans/5.0/ref/settings/#email-backend
EMAIL_BACKEND = ('django.core.mail.backends.smtp.EmailBackend'
                 if not DEBUG
                 else 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = 'localhost'
EMAIL_HOST_PASSWORD = ''
EMAIL_HOST_USER = ''
EMAIL_PORT = ''
EMAIL_SUBJECT_PREFIX = '[Django] '
EMAIL_USE_LOCALTIME = True
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
EMAIL_SSL_CERTFILE = None
EMAIL_SSL_KEYFILE = None


# allauth
# regular account config doc -> https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_PASSWORD_MIN_LENGTH = 6 if not DEBUG else 3
# 是否发邮件: mandatory:发邮件且必须验证才能登录, optional:发邮件, none:不发
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_CHANGE_EMAIL = True


# Celery Config
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'default'

# LOG
LOG_PATH = config.LOG_PATH
LOG_PATH.mkdir(parents=True, exist_ok=True)
LOG_LEVEL = 'INFO'
DJANGO_STRUCTLOG_CELERY_ENABLED = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json_formatter': {
            '()': structlog.stdlib.ProcessorFormatter,
            'processor': structlog.processors.JSONRenderer(),
            # 'processor': MsgspecJSONRenderer(),
        },
        'plain_console': {
            '()': structlog.stdlib.ProcessorFormatter,
            'processor': structlog.dev.ConsoleRenderer(),
        },
        'key_value': {
            '()': structlog.stdlib.ProcessorFormatter,
            'processor': structlog.processors.KeyValueRenderer(key_order=['timestamp', 'level', 'event', 'logger']),
        },
    },
    'filters': {},
    'handlers': {
        # 'json_file': {
        #     'level': LOG_LEVEL,
        #     'formatter': 'json_formatter',
        #     'class': 'utils.log.DayRotateHandlerWithThread',
        #     'file_name': LOG_PATH / 'json.log',
        #     'backup_count': 15,
        #     'when': 'day',
        # },
        'django_file': {
            'level': LOG_LEVEL,
            'formatter': 'key_value',
            'class': 'utils.log.DayRotateHandlerWithThread',
            'file_name': LOG_PATH / 'django.log',
            'backup_count': 15,
            'when': 'day',
        },
        'api_file': {
            'level': LOG_LEVEL,
            'formatter': 'key_value',
            'class': 'utils.log.DayRotateHandlerWithThread',
            'file_name': LOG_PATH / 'api.log',
            'backup_count': 15,
            'when': 'day',
        },
        'db_file': {
            'level': LOG_LEVEL,
            'formatter': 'key_value',
            'class': 'utils.log.DayRotateHandlerWithThread',
            'file_name': LOG_PATH / 'db.log',
            'backup_count': 15,
            'when': 'day',
        },
        'beat_file': {
            'level': LOG_LEVEL,
            'formatter': 'key_value',
            'class': 'utils.log.DayRotateHandlerWithThread',
            'file_name': LOG_PATH / 'beat.log',
            'backup_count': 15,
            'when': 'day',
        },
        'worker_file': {
            'level': LOG_LEVEL,
            'formatter': 'key_value',
            'class': 'utils.log.DayRotateHandlerWithThread',
            'file_name': LOG_PATH / 'worker.log',
            'backup_count': 15,
            'when': 'day',
        },
        'console': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'plain_console',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'django_file'],
            'level': LOG_LEVEL,
        },
        'django.db.backends': {
            'handlers': ['db_file'],
            'level': LOG_LEVEL,
        },
        'django_structlog': {
            'handlers': ['console', 'api_file'],
            'level': LOG_LEVEL,
        },
        'api': {
            'handlers': ['console', 'api_file'],
            'level': LOG_LEVEL,
        },
        'worker': {
            'handlers': ['console', 'worker_file'],
            'level': LOG_LEVEL,
        },
        'beat': {
            'handlers': ['console', 'beat_file'],
            'level': LOG_LEVEL,
        },
    },
}
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)
