from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from auth_app.models import User
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

