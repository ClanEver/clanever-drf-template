import pytest
from admin_patch.models import User
from django.test import Client


@pytest.fixture
def admin(db):  # noqa: ARG001
    return User.objects.create_user(username='admin', password='admin', is_superuser=True)


@pytest.fixture
def admin_client(client: Client, admin: User):
    client.force_login(admin)
    return client
