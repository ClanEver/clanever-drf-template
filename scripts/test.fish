set SCRIPT_DIR (status dirname)
cd $SCRIPT_DIR && cd ..

mkdir -p test_dir
cd test_dir
rm -rf my-django-project

cookiecutter ../ --no-input
cd my-django-project
rye run dev_mnm

source .venv/bin/activate.fish

echo "
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_superuser('admin', 'admin@example.com', 'admin')
" | python manage.py shell

echo "
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_user(username='testuser', email='staff@example.com', password='testuser', is_staff=True)
" | python manage.py shell

rye run dev 38888
