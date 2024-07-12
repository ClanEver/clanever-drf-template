from django.core.exceptions import ValidationError
from django.test import TestCase, Client

from {{ cookiecutter.app_name }}.models import {{ cookiecutter.model_name }}

# Create your tests here.

class {{ cookiecutter.model_name }}Tests(TestCase):
    def test_example(self):
        with self.assertRaises(ValidationError):
            raise ValidationError('test')


class {{ cookiecutter.model_name }}ViewSetTests(TestCase):
    def test_example(self):
        with self.assertRaises(ValidationError):
            raise ValidationError('test')
