let SCRIPT_DIR = ($env.CURRENT_FILE | path dirname)
cd $SCRIPT_DIR
cd ..

mkdir test_dir
cd test_dir
rm -rf my-django-project

cookiecutter ../ --no-input
cd my-django-project

mise trust mise.toml
mise run db-clean
mise run db-up-d
mise run mnm
uv run -- pytest
mise run all
