# {{ cookiecutter.project_name }}

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
- [drf-spectacular](https://github.com/tfranzel/drf-spectacular) [[Doc](https://drf-spectacular.readthedocs.io/en/latest/)]
- [django-allauth](https://github.com/pennersr/django-allauth) [[Doc](https://docs.allauth.org/en/latest/)]

## Utility Libraries

- [arrow](https://github.com/arrow-py/arrow) [[Doc](https://arrow.readthedocs.io/en/latest/)]
- [moremore-itertools](https://github.com/more-itertools/more-itertools) [[Doc](https://more-itertools.readthedocs.io/en/latest/)]
- [msgspec](https://github.com/jcrist/msgspec) [[Doc](https://jcristharif.com/msgspec/)]
- [requests](https://github.com/psf/requests) [[Doc](https://requests.readthedocs.io/en/latest/)]
- [tenacity](https://github.com/jd/tenacity) [[Doc](https://tenacity.readthedocs.io/en/latest/)]

## Admin (with simpleui)

References

- [Official doc](https://docs.djangoproject.com/en/5.1/ref/contrib/admin/)
- [simpleui doc](https://github.com/newpanjing/simpleui)

For non-DEBUG mode, static files need to be collected and handled by Nginx / Caddy

Note the STATIC_ROOT configuration in settings

```shell
python manage.py collectstatic
```

## Celery

```shell
# Start worker
rye run dev_cw
celery -A {{ cookiecutter.project_slug }} worker -l INFO -c 2 -Q default -n default@%h
# Start beat
# Only 1 instance of beat is needed
rye run dev_cb
celery -A {{ cookiecutter.project_slug }} beat -l INFO
```