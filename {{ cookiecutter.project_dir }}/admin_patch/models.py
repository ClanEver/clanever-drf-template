import httpx
from authlib.integrations.httpx_client import OAuth2Client
from authlib.jose import JsonWebKey
from authlib.oidc.discovery import get_well_known_url
from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from utils.db import BaseModel

username_validator = validators.RegexValidator(
    r'^[a-zA-Z0-9]{4,100}$',
    '4-100位，字母或数字',
)
oidc_name_validator = validators.RegexValidator(
    r'^[a-zA-Z0-9]{1,100}$',
    '1-100位，字母或数字',
)


class User(AbstractUser):
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text='4-100位，字母或数字',
        validators=[username_validator],
        error_messages={
            'unique': _('A user with that username already exists.'),
        },
    )
    password = models.TextField(_('password'), blank=True)
    # 为了兼容且最小修改 把 first_name 作为 nickname
    first_name = models.CharField('昵称', max_length=150, blank=True)
    last_name = models.CharField('备用名', max_length=150, blank=True)

    @property
    def nickname(self):
        return self.first_name

    @nickname.setter
    def nickname(self, val):
        self.first_name = val


class OidcProvider(BaseModel):
    name = models.CharField(verbose_name='名称', max_length=100, unique=True, validators=[oidc_name_validator], help_text='仅字母或数字')
    client_id = models.CharField()
    client_secret = models.CharField()
    base_url = models.URLField(help_text='示例: https://authentik.example.com/application/o/app_name/')
    private_key = models.TextField(verbose_name='私钥', blank=True, help_text='如果供应者开启了加密, 则需要填入 pem 密钥')
    cache_expire_length = models.IntegerField(verbose_name='缓存过期时间 (s)', default=600, help_text='对象在内存缓存中缓存的时长, 生产环境可以改长一些')
    icon_url = models.URLField('图标 url', blank=True, help_text='供应商图标图片 url, 应优先使用此字段, 其次使用图标名')
    icon_name = models.CharField('图标名', blank=True, help_text=mark_safe('Material Icon 名称, 示例: login, 参考: <a href="https://fonts.google.com/icons" class="text-primary-600 dark:text-primary-500">https://fonts.google.com/icons</a>'))

    _well_known: dict
    _jwks: dict

    class Meta:
        verbose_name = 'OIDC 服务'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    @property
    def well_known(self):
        if not getattr(self, '_well_known', None):
            url = get_well_known_url(self.base_url, True)
            self._well_known = httpx.get(url).json()
        return self._well_known

    @property
    def jwks(self):
        if not getattr(self, '_jwks', None):
            url = self.well_known['jwks_uri']
            self._jwks = httpx.get(url).json()
        return self._jwks

    @property
    def key_set(self):
        return JsonWebKey.import_key_set(self.jwks)

    @property
    def client(self):
        if not getattr(self, '_client', None):
            self._client = OAuth2Client(
                client_id=self.client_id,
                client_secret=self.client_secret,
                code_challenge_method='S256',
            )
        return self._client


class OidcUser(BaseModel):
    provider = models.ForeignKey(OidcProvider, on_delete=models.CASCADE)
    sub = models.CharField()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    oidc_info = models.JSONField(verbose_name='oidc信息')
    last_login = models.DateTimeField(verbose_name='上次登录时间', blank=True, null=True)

    class Meta:
        verbose_name = 'OIDC 用户关联'
        verbose_name_plural = verbose_name
        constraints = [models.UniqueConstraint(fields=['provider', 'sub'], name='oidc_user_unique_provider_sub')]

    def __str__(self):
        return f'{self.provider.name} - {self.user.nickname}'
