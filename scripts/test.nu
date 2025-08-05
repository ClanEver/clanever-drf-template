let SCRIPT_DIR = ($env.CURRENT_FILE | path dirname)
cd $SCRIPT_DIR
cd ..

mkdir test_dir
cd test_dir
rm -rf my-django-project

cookiecutter ../ --no-input
cd my-django-project

mise trust mise.toml
mise run dev_db_clean
mise run dev_db_up_d
sleep 3
mise run dev_mnm
mise run dev
