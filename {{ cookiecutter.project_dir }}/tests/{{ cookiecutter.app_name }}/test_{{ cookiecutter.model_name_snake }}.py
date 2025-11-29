import pytest
from django.urls import reverse

# Create your tests here.

@pytest.mark.django_db
def test_list_{{ cookiecutter.model_name_snake }}(admin_client):
    response = admin_client.get(reverse('{{ cookiecutter.app_name }}:{{ cookiecutter.model_name_snake }}-list'))
    assert response.status_code == 200
