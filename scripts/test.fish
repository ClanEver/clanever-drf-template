set SCRIPT_DIR (status dirname)
cd $SCRIPT_DIR && cd ..

mkdir -p test_dir
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
