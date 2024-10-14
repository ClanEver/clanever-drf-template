'''
For more information on this file, see
https://docs.djangoproject.com/zh-hans/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/zh-hans/5.1/ref/settings/
'''

import logging
import os
from pathlib import Path

from import_export.formats.base_formats import CSV, DEFAULT_FORMATS
from kombu import Queue

from {{ cookiecutter.project_slug }}.log_setting import gen_log_setting

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------- Custom Settings ----------------
class __BaseConfig:  # noqa: N801
    DEBUG: bool = False
    ALLOWED_HOSTS: list[str] = ['*']
    DATABASES: dict = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        },
    }
    LOG_PATH = BASE_DIR / 'logs'
    REDIS_URL: str = 'redis://:@127.0.0.1:6379/0'  # TODO
    FLOWER_URL: str = 'http://127.0.0.1:5555'


class DevConfig(__BaseConfig):
    DEBUG = True
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        },
    }


class TestConfig(__BaseConfig):
    pass


class ProdConfig(__BaseConfig):
    ALLOWED_HOSTS = ['TODO']
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'mydatabase',
            'USER': 'mydatabaseuser',
            'PASSWORD': 'mypassword',
            'HOST': '127.0.0.1',
            'PORT': '5432',
            'OPTIONS': {
                # 连接池参数参考 https://www.psycopg.org/psycopg3/docs/api/pool.html#the-connectionpool-class
                'pool': {
                    'min_size': 2,
                    'max_size': 5,
                    'timeout': 10,
                },
            },
        },
    }
    REDIS_URL = 'TODO'


DJANGO_CONFIG = os.environ.get('DJANGO_CONFIG', 'dev')
config = {
    'dev': DevConfig,
    'test': TestConfig,
    'prod': ProdConfig,
}.get(DJANGO_CONFIG)


# ---------------- Django Settings ----------------
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/zh-hans/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-!!!SET DJANGO_SECRET_KEY!!!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config.DEBUG

ALLOWED_HOSTS = config.ALLOWED_HOSTS

# Application definition
SITE_ID = 1
INSTALLED_APPS = [
    'auth_app',
    'simpleui',
    # django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # third-party
    'django_structlog',
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
    'import_export',
    # other
    'debug',
    # your apps
    '{{ cookiecutter.app_name }}',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django_structlog.middlewares.RequestMiddleware',
    'utils.midware.Wrap5xxErrorMiddleware',
    'django_structlog.middlewares.RequestMiddleware',
    'utils.midware.Log5xxErrorMiddleware',
    'utils.midware.LogAPIExceptionMiddleware',
]

ROOT_URLCONF = '{{ cookiecutter.project_slug }}.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
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
# https://docs.djangoproject.com/zh-hans/5.1/ref/settings/#databases

DATABASES = config.DATABASES
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': config.REDIS_URL,
        'OPTIONS': {
            'pool_class': 'redis.BlockingConnectionPool',
            'max_connections': 10,
        },
    },
}

# Password validation
# https://docs.djangoproject.com/zh-hans/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [] if DEBUG else [
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
]

# Internationalization
# https://docs.djangoproject.com/zh-hans/5.1/topics/i18n/

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/zh-hans/5.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
# 生产环境应交给 Nginx / Caddy 处理
# Should be handled by Nginx / Caddy in production environment
STATIC_ROOT = BASE_DIR / 'static_root'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/zh-hans/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'auth_app.User'


# ---------------- DRF Settings ----------------
# REST_FRAMEWORK
REST_FRAMEWORK = {
    # authentication
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
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
        *(['rest_framework.renderers.BrowsableAPIRenderer'] if DEBUG else []),
    ],
    'DEFAULT_PARSER_CLASSES': [
        'utils.drf_msgspec_json.MsgspecJSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    # other
    'EXCEPTION_HANDLER': 'utils.view.exception_handler',
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
    'SCHEMA_PATH_PREFIX': r'/api/',  # swagger api 分组前缀
    'SERVE_PERMISSIONS': ['auth_app.permissions.IsSuperUser'],
}


# ---------------- Django Email Settings ----------------
# email config -> https://docs.djangoproject.com/zh-hans/5.1/ref/settings/#email-backend
EMAIL_BACKEND = ('django.core.mail.backends.console.EmailBackend'
                 if DEBUG
                 else 'django.core.mail.backends.smtp.EmailBackend')
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


# ---------------- Allauth Settings ----------------
# regular account config doc -> https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_PASSWORD_MIN_LENGTH = 3 if DEBUG else 8
# 是否发邮件: mandatory:发邮件且必须验证才能登录, optional:发邮件, none:不发
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_CHANGE_EMAIL = True


# ---------------- Celery Settings ----------------
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_RESULT_EXTENDED = True
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'default'
CELERY_BROKER_URL = config.REDIS_URL
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'
CELERY_BROKER_CONNECTION_RETRY = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
# 每个工作进程处理的最大任务数
# Maximum number of tasks per worker process
CELERY_WORKER_MAX_TASKS_PER_CHILD = 500
# 每个工作进程的最大内存使用量
# Maximum memory usage per worker process
CELERY_WORKER_MAX_MEMORY_PER_CHILD = 150 * 1024  # 150MB
CELERY_TASK_QUEUES = (
    Queue('celery', routing_key='celery'),
    Queue('priority', routing_key='priority'),
)
# for reverse proxy
FLOWER_URL = config.FLOWER_URL


# ---------------- Log Settings ----------------
LOG_PATH = config.LOG_PATH
LOG_PATH.mkdir(parents=True, exist_ok=True)
LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO
LOGGING = gen_log_setting(LOG_PATH, LOG_LEVEL, DEBUG)

DJANGO_STRUCTLOG_CELERY_ENABLED = True
DJANGO_STRUCTLOG_STATUS_4XX_LOG_LEVEL = logging.WARNING


# ---------------- Django Import Export Settings ----------------
# https://django-import-export.readthedocs.io/en/latest/installation.html#settings
IMPORT_FORMATS = [CSV]
EXPORT_FORMATS = DEFAULT_FORMATS


# ---------------- SimpleUI Settings ----------------
# https://newpanjing.github.io/simpleui_docs/config.html#%E8%8F%9C%E5%8D%95
SIMPLEUI_CONFIG = {
    'system_keep': True,
    'menus': [
        {
            'name': '其他',
            'icon': 'fa fa-file',
            # 二级菜单
            # sub menu
            'models': [
                {
                    'name': 'Swagger',
                    'icon': 'fa-solid fa-cubes',
                    'url': '/api/schema/swagger-ui/',
                },
                {
                    'name': 'Redoc',
                    'icon': 'fa-solid fa-book',
                    'url': '/api/schema/redoc/',
                },
                {
                    'name': 'Flower',
                    'icon': 'fa-solid fa-seedling',
                    'url': '/flower/',
                },
                {
                    'name': '网站主页',
                    'icon': 'fas fa-home',
                    'url': '/',
                },
            ],
        },
    ],
}
