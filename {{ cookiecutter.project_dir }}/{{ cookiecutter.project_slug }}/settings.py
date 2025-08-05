"""
For more information on this file, see
https://docs.djangoproject.com/zh-hans/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/zh-hans/5.1/ref/settings/
"""

import logging
import os
from datetime import timedelta
from pathlib import Path

from django.urls import reverse_lazy
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
    REDIS_URL: str = 'redis://:@127.0.0.1:6379/0'
    FLOWER_URL: str = 'http://127.0.0.1:5555'


class DevConfig(__BaseConfig):
    DEBUG = True
    REDIS_URL: str = 'redis://:@127.0.0.1:26379/0'
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'django_db',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'HOST': '127.0.0.1',
            'PORT': '25432',
            'OPTIONS': {
                # 连接池参数参考 https://www.psycopg.org/psycopg3/docs/api/pool.html#the-connectionpool-class
                'pool': {
                    'min_size': 2,
                    'max_size': 5,
                    'timeout': 10,
                },
                'options': '-c idle_in_transaction_session_timeout=30s',
            },
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
                'options': '-c idle_in_transaction_session_timeout=30s',
            },
        },
    }
    REDIS_URL = 'TODO'


DJANGO_CONFIG = os.environ.get('DJANGO_CONFIG', 'dev')
config: type[__BaseConfig] = {
    'dev': DevConfig,
    'test': TestConfig,
    'prod': ProdConfig,
}[DJANGO_CONFIG]


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
    # --- unfold admin ---
    'unfold',
    'unfold.contrib.filters',  # optional, if special filters are needed
    'unfold.contrib.forms',  # optional, if special form elements are needed
    'unfold.contrib.inlines',  # optional, if special inlines are needed
    'unfold.contrib.import_export',  # optional, if django-import-export package is used
    # "unfold.contrib.guardian",  # optional, if django-guardian package is used
    # "unfold.contrib.simple_history",  # optional, if django-simple-history package is used
    # --- django ---
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    # 'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # --- third party ---
    'django_structlog',
    'django_filters',
    'rest_framework',
    'knox',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'django_celery_results',
    'django_celery_beat',
    'import_export',
    'admin_patch',
    # --- your apps ---
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
        'KEY_PREFIX': '{{ cookiecutter.project_name|trim() }}',
    },
}
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'  # session 使用缓存

# Password validation
# https://docs.djangoproject.com/zh-hans/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [] if DEBUG else [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
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

# Email
# https://docs.djangoproject.com/zh-hans/5.1/ref/settings/#email-backend
EMAIL_BACKEND = (
    'django.core.mail.backends.console.EmailBackend' if DEBUG else 'django.core.mail.backends.smtp.EmailBackend'
)
EMAIL_HOST = 'localhost'
EMAIL_HOST_PASSWORD = ''
EMAIL_HOST_USER = ''
EMAIL_PORT = ''
EMAIL_SUBJECT_PREFIX = '[{{ cookiecutter.project_name }}] '
EMAIL_USE_LOCALTIME = True
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
EMAIL_SSL_CERTFILE = None
EMAIL_SSL_KEYFILE = None

# Auth
# https://docs.djangoproject.com/zh-hans/5.1/ref/settings/#auth
AUTH_USER_MODEL = 'admin_patch.User'
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/profile/'
LOGOUT_REDIRECT_URL = None
PASSWORD_RESET_TIMEOUT = 60 * 30  # 30m

# ---------------- DRF Settings ----------------
REST_FRAMEWORK = {
    # authentication
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'knox.auth.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # pagination
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_RENDERER_CLASSES': [
        # msgspec
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

# ---------------- django-rest-knox ----------------
REST_KNOX = {
    'SECURE_HASH_ALGORITHM': 'hashlib.sha512',
    'AUTH_TOKEN_CHARACTER_LENGTH': 64,
    'TOKEN_TTL': timedelta(hours=24),
    'TOKEN_LIMIT_PER_USER': 2,
    'AUTO_REFRESH': True,
    'AUTO_REFRESH_MAX_TTL': None,
    'MIN_REFRESH_INTERVAL': 60 * 10,  # seconds
}

# ---------------- drf-spectacular ----------------
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
    'SERVE_PERMISSIONS': ['utils.permission.IsSuperUser'],
    'COMPONENT_SPLIT_REQUEST': True,  # 在适当的情况下将组件分为请求和响应部分
    'SORT_OPERATION_PARAMETERS': False,  # params 是否按字母顺序排序
    'POSTPROCESSING_HOOKS': [
        'drf_spectacular.hooks.postprocess_schema_enums',
        'utils.drf_spectacular.postprocess_default_error_response',
    ],
}

# ---------------- Celery ----------------
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_RESULT_EXTENDED = True
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'default'
CELERY_BROKER_URL = config.REDIS_URL
CELERY_BROKER_CONNECTION_RETRY = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BROKER_TRANSPORT_OPTIONS = {'global_keyprefix': '{{ cookiecutter.project_name|trim() }}:'}
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'
# 每个工作进程处理的最大任务数
CELERY_WORKER_MAX_TASKS_PER_CHILD = 500
# 每个工作进程的最大内存使用量
CELERY_WORKER_MAX_MEMORY_PER_CHILD = 150 * 1024  # 150MB
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_QUEUES = (
    Queue('default', routing_key='default'),
    Queue('priority', routing_key='priority'),
)
# for reverse proxy
FLOWER_URL = config.FLOWER_URL

# ---------------- Log ----------------
LOG_PATH = config.LOG_PATH
LOG_PATH.mkdir(parents=True, exist_ok=True)
LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO
LOG_BACKUP_DAYS = 15
LOGGING = gen_log_setting(LOG_PATH, LOG_LEVEL, DEBUG, LOG_BACKUP_DAYS)

DJANGO_STRUCTLOG_CELERY_ENABLED = True
DJANGO_STRUCTLOG_STATUS_4XX_LOG_LEVEL = logging.WARNING

# ---------------- Django Import Export ----------------
# https://django-import-export.readthedocs.io/en/latest/installation.html#settings
IMPORT_FORMATS = [CSV]
EXPORT_FORMATS = DEFAULT_FORMATS

# ---------------- Unfold Admin ----------------
# https://unfoldadmin.com/docs/configuration/settings/
def menu_model_item(title: str, app: str, model: str, icon: str, permission=None, **kwargs):
    return {
        'title': title or model,
        'icon': icon,
        'link': reverse_lazy(f'admin:{app}_{model}_changelist'.lower()),
        'permission': permission or (
            lambda request: request.user.is_superuser or request.user.has_perm(f'view_{model}'.lower())),
        **kwargs,
    }


UNFOLD = {
    "SITE_TITLE": "{{ cookiecutter.project_name|trim() }} Admin",  # 网页标题尾缀
    "SITE_HEADER": "{{ cookiecutter.project_name|trim() }} Admin",  # 侧边栏标题
    "SITE_SUBHEADER": "",  # 侧边栏副标题
    "SITE_SYMBOL": "space_dashboard",  # 侧边栏图标名 参考: https://fonts.google.com/icons
    'SIDEBAR': {
        'show_search': True,
        'show_all_applications': lambda request: request.user.is_superuser,
        'navigation': [
            {
                'separator': False,  # 分隔线
                'collapsible': False,  # 可折叠
                'items': [
                    {
                        'title': '主页',
                        'icon': 'home',  # 图标名 参考: https://fonts.google.com/icons
                        'link': reverse_lazy('admin:index'),
                        'permission': lambda request: request.user.is_staff,
                        # "badge": "sample_app.badge_callback",
                    },
                ],
            },
            {
                'title': '{{ cookiecutter.app_name|to_camel }}',
                'separator': False,
                'collapsible': False,
                'items': [
                    menu_model_item('', '{{ cookiecutter.app_name }}', '{{ cookiecutter.model_name }}', 'topic'),
                ],
            },
            {
                'title': '用户与权限',
                'separator': True,
                'collapsible': True,
                'items': [
                    menu_model_item('用户', 'admin_patch', 'user', 'person'),
                    menu_model_item('角色', 'admin_patch', 'GroupP', 'group'),
                    menu_model_item('权限', 'admin_patch', 'PermissionP', 'category'),
                    menu_model_item('登录 Token', 'knox', 'AuthToken', 'where_to_vote'),
                    menu_model_item('OIDC 服务', 'admin_patch', 'OidcProvider', 'cloud_circle'),
                    menu_model_item('OIDC 用户关联', 'admin_patch', 'OidcUser', 'account_circle'),
                ],
            },
            {
                'title': 'Celery',
                'separator': True,
                'collapsible': True,
                'items': [
                    menu_model_item('任务', 'admin_patch', 'PeriodicTaskP', 'task'),
                    menu_model_item('调度器 - Crontab', 'admin_patch', 'CrontabScheduleP', 'update'),
                    menu_model_item('调度器 - 间隔', 'admin_patch', 'IntervalScheduleP', 'arrow_range'),
                    menu_model_item('调度器 - 定时', 'admin_patch', 'ClockedScheduleP', 'hourglass_bottom'),
                    menu_model_item('调度器 - 天文事件', 'admin_patch', 'SolarScheduleP', 'event'),
                    menu_model_item('任务结果', 'admin_patch', 'TaskResultP', 'draft'),
                    menu_model_item('任务组结果', 'admin_patch', 'GroupResultP', 'file_copy'),
                ],
            },
            {
                'title': '开发工具',
                'separator': True,
                'collapsible': True,
                'items': [
                    {
                        'title': 'Swagger',
                        'icon': 'data_object',
                        'link': '/admin/dev_tools/swagger/',
                        'permission': lambda request: request.user.is_superuser,
                    },
                    {
                        'title': 'Redoc',
                        'icon': 'note_stack',
                        'link': '/admin/dev_tools/redoc/',
                        'permission': lambda request: request.user.is_superuser,
                    },
                    {
                        'title': 'Scalar',
                        'icon': 'shuffle',
                        'link': '/admin/dev_tools/scalar/',
                        'permission': lambda request: request.user.is_superuser,
                    },
                    {
                        'title': 'Flower',
                        'icon': 'deceased',
                        'link': '/admin/dev_tools/flower/',
                        'permission': lambda request: request.user.is_superuser,
                    },
                ],
            },
        ],
    },
}

# ---------------- django-revproxy ----------------
REVPROXY = {
    'QUOTE_SPACES_AS_PLUS': True,
}
