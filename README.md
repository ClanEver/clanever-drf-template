# ClanEver DRF Template

Powered by [cookiecutter](https://github.com/cookiecutter/cookiecutter)

A simple drf template. Initialize a Django project skipping steps such as `rye init` and `django-admin startproject xxx`.

## Usage

install cookiecutter
```shell
pip install cookiecutter jinja2-strcase
```

or use [rye](https://github.com/mitsuhiko/rye) to install
```shell
rye install cookiecutter --extra-requirement jinja2-strcase
```

use this template
```shell
cookiecutter https://github.com/ClanEver/clanever-drf-template.git
```

use app template
```shell
rye run startapp
# or
cookiecutter https://github.com/ClanEver/clanever-drf-app-template.git
```

## Relation

[clanever-drf-app-template](https://github.com/ClanEver/clanever-drf-app-template/)

## License

[MIT](./LICENSE)
