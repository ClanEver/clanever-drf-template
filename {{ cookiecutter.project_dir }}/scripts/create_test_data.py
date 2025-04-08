import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_django_project.settings')
django.setup()
from admin_patch.models import User, OidcProvider


if __name__ == '__main__':
    if admin := User.objects.filter(username='admin').first():
        print('admin user already exists')
    else:
        admin = User.objects.create_superuser(username='admin', password='admin')
        print('admin user created')
