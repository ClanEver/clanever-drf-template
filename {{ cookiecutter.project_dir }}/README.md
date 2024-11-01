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
    - [django-rest-knox](https://github.com/jazzband/django-rest-knox) [[文档](https://jazzband.github.io/django-rest-knox/)]
- [drf-spectacular](https://github.com/tfranzel/drf-spectacular) [[文档](https://drf-spectacular.readthedocs.io/en/latest/)]

## 工具库

- [arrow](https://github.com/arrow-py/arrow) [[文档](https://arrow.readthedocs.io/en/latest/)]
- [more-itertools](https://github.com/more-itertools/more-itertools) [[文档](https://more-itertools.readthedocs.io/en/latest/)]
- [msgspec](https://github.com/jcrist/msgspec) [[文档](https://jcristharif.com/msgspec/)]
- [requests](https://github.com/psf/requests) [[文档](https://requests.readthedocs.io/en/latest/)]
- [tenacity](https://github.com/jd/tenacity) [[文档](https://tenacity.readthedocs.io/en/latest/)]

## Admin (with simpleui)

参考

- [官方文档](https://docs.djangoproject.com/zh-hans/5.1/ref/contrib/admin/)
- [simpleui 文档](https://newpanjing.github.io/simpleui_docs/config.html)

若为非 DEBUG 模式，需要收集静态文件交给 Nginx / Caddy 处理

注意 settings 中的 STATIC_ROOT 配置

```shell
python manage.py collectstatic
```

## Celery

```shell
# 启动 worker
rye run dev_c_worker
# 或指定队列
rye run dev_c_worker -Q celery,priority
# 或
celery -A {{ cookiecutter.project_slug }} worker -l INFO -c 2 -Q celery -P solo
# 注意 -P solo 为单进程模式，不适用于生产环境
# 生产应不设置（等同于使用 prefork）或 gevent（需要安装）

# 启动 beat
# beat 只需要 1 个实例
rye run dev_c_beat
# 或
celery -A {{ cookiecutter.project_slug }} beat -l INFO

# 启动 flower
rye run dev_c_flower
# or
celery -A {{ cookiecutter.project_slug }} flower --address=127.0.0.1 --url_prefix=flower

# 如果使用 fish shell, 可以同时启动 worker, beat, flower
rye run dev_c
```
