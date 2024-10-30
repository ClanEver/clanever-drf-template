let SCRIPT_DIR = ($env.CURRENT_FILE | path dirname)
cd $SCRIPT_DIR
cd ..

mkdir test_dir
cd test_dir
rm -rf my-django-project

cookiecutter ../ --no-input
cd my-django-project
rye run dev_mnm

let VENV_PYTHON = ".venv/bin/python"

^$VENV_PYTHON manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_superuser('admin', 'admin@example.com', 'admin')"

^$VENV_PYTHON manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_user(username='testuser', email='staff@example.com', password='testuser', is_staff=True)"

rye run dev 38888
