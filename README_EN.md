# ClanEver DRF Template

A simple drf template. Initialize a Django project skipping steps such as `rye init` and `django-admin startproject xxx`.

Powered by [cookiecutter](https://github.com/cookiecutter/cookiecutter) and [rye](https://github.com/mitsuhiko/rye)

## Integration

- [celery](https://github.com/celery/celery) [[Doc](https://docs.celeryq.dev/en/stable/) | [Doc With Django](https://docs.celeryq.dev/en/stable/django/index.html)]
    - [django-celery-beat](https://github.com/celery/django-celery-beat)
    - [django-celery-results](https://github.com/celery/django-celery-results)
    - [flower](https://github.com/mher/flower) [[Doc](https://flower.readthedocs.io/en/latest/)]
- [simpleui](https://github.com/newpanjing/simpleui) [[Doc](https://newpanjing.github.io/simpleui_docs/config.html)]
- [django-import-export](https://github.com/django-import-export/django-import-export) [[Doc](https://django-import-export.readthedocs.io/en/latest/)]
- [django-structlog](https://github.com/jrobichaud/django-structlog) [[Doc](https://django-structlog.readthedocs.io/en/latest/)]
    - [structlog](https://github.com/hynek/structlog) [[Doc](https://www.structlog.org/en/stable/)]
- [django-rest-framework](https://github.com/encode/django-rest-framework/tree/master) [[Doc](https://www.django-rest-framework.org/)]
    - [dj-rest-auth](https://github.com/iMerica/dj-rest-auth) [[Doc](https://dj-rest-auth.readthedocs.io/en/latest/)]
    - [django-rest-knox](https://github.com/jazzband/django-rest-knox) [[Doc](https://jazzband.github.io/django-rest-knox/)]
- [drf-spectacular](https://github.com/tfranzel/drf-spectacular) [[Doc](https://drf-spectacular.readthedocs.io/en/latest/)]

## Utility Libraries

- [arrow](https://github.com/arrow-py/arrow) [[Doc](https://arrow.readthedocs.io/en/latest/)]
- [more-itertools](https://github.com/more-itertools/more-itertools) [[Doc](https://more-itertools.readthedocs.io/en/latest/)]
- [msgspec](https://github.com/jcrist/msgspec) [[Doc](https://jcristharif.com/msgspec/)]
- [requests](https://github.com/psf/requests) [[Doc](https://requests.readthedocs.io/en/latest/)]
- [tenacity](https://github.com/jd/tenacity) [[Doc](https://tenacity.readthedocs.io/en/latest/)]

## Usage

1. Install [rye](https://github.com/mitsuhiko/rye)

2. Use rye to install cookiecutter
    ```shell
    rye install cookiecutter --extra-requirement jinja2-strcase
    ```

3. Use this template
    ```shell
    cookiecutter https://github.com/ClanEver/clanever-drf-template.git
    ```

4. Change settings.py then run in dev
    ```shell
    # make migrations and migrate
    rye run dev_mnm
    # runserver
    rye run dev
    ```

5. [Optional] Use app template
    ```shell
    rye run startapp
    # or
    cookiecutter https://github.com/ClanEver/clanever-drf-app-template.git
    ```

## Relation

[clanever-drf-app-template](https://github.com/ClanEver/clanever-drf-app-template/)

## License

[MIT](./LICENSE)
