# {{ cookiecutter.project_name|trim() }}

## 集成

- [celery](https://github.com/celery/celery) [[文档](https://docs.celeryq.dev/en/stable/) | [文档 With Django](https://docs.celeryq.dev/en/stable/django/index.html)]
    - [django-celery-beat](https://github.com/celery/django-celery-beat)
    - [django-celery-results](https://github.com/celery/django-celery-results)
    - [flower](https://github.com/mher/flower) [[文档](https://flower.readthedocs.io/en/latest/)]
- [simpleui](https://github.com/newpanjing/simpleui) [[文档](https://newpanjing.github.io/simpleui_docs/config.html)]
- [django-import-export](https://github.com/django-import-export/django-import-export) [[文档](https://django-import-export.readthedocs.io/en/latest/)]
- [django-structlog](https://github.com/jrobichaud/django-structlog) [[文档](https://django-structlog.readthedocs.io/en/latest/)]
    - [structlog](https://github.com/hynek/structlog) [[文档](https://www.structlog.org/en/stable/)]
- [django-rest-framework](https://github.com/encode/django-rest-framework/tree/master) [[文档](https://www.django-rest-framework.org/)]
    - [dj-rest-auth](https://github.com/iMerica/dj-rest-auth) [[文档](https://dj-rest-auth.readthedocs.io/en/latest/)]
- [drf-spectacular](https://github.com/tfranzel/drf-spectacular) [[文档](https://drf-spectacular.readthedocs.io/en/latest/)]
- [django-allauth](https://github.com/pennersr/django-allauth) [[文档](https://docs.allauth.org/en/latest/)]

## 工具库

- [arrow](https://github.com/arrow-py/arrow) [[文档](https://arrow.readthedocs.io/en/latest/)]
- [moremore-itertools](https://github.com/more-itertools/more-itertools) [[文档](https://more-itertools.readthedocs.io/en/latest/)]
- [msgspec](https://github.com/jcrist/msgspec) [[文档](https://jcristharif.com/msgspec/)]
- [requests](https://github.com/psf/requests) [[文档](https://requests.readthedocs.io/en/latest/)]
- [tenacity](https://github.com/jd/tenacity) [[文档](https://tenacity.readthedocs.io/en/latest/)]

## Admin (with simpleui)

参考

- [官方文档](https://docs.djangoproject.com/zh-hans/5.1/ref/contrib/admin/)
- [simpleui 文档](https://github.com/newpanjing/simpleui)

若为非 DEBUG 模式，需要收集静态文件交给 Nginx / Caddy 处理

注意 settings 中的 STATIC_ROOT 配置

```shell
python manage.py collectstatic
```

## Celery

```shell
# 启动 worker
rye run dev_cw
# 或
celery -A {{ cookiecutter.project_slug }} worker -l INFO -c 2 -Q default -n default@%h

# 启动 beat
# beat 只需要 1 个实例
rye run dev_cb
# 或
celery -A {{ cookiecutter.project_slug }} beat -l INFO
```
