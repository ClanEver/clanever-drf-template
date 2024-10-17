from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models
from django.utils.translation import gettext_lazy as _

custom_username_validator = validators.RegexValidator(
    r'^[a-zA-Z0-9]{5,100}$',
    '5-100位，字母或数字',
)


class User(AbstractUser):
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text='5-100位，字母或数字',
        validators=[custom_username_validator],
        error_messages={
            'unique': _('A user with that username already exists.'),
        },
    )
