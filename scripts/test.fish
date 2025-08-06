set SCRIPT_DIR (status dirname)
cd $SCRIPT_DIR && cd ..

mkdir -p test_dir
cd test_dir
rm -rf my-django-project

cookiecutter ../ --no-input
cd my-django-project

mise trust mise.toml
mise run dev_db_clean
mise run dev_db_up_d
mise run dev_mnm
mise run dev
