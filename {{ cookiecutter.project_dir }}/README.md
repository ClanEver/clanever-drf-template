# {{ cookiecutter.project_name|trim() }}

## 集成

- [celery](https://github.com/celery/celery) [[文档](https://docs.celeryq.dev/en/stable/) | [文档 With Django](https://docs.celeryq.dev/en/stable/django/index.html)]
    - [django-celery-beat](https://github.com/celery/django-celery-beat)
    - [django-celery-results](https://github.com/celery/django-celery-results)
    - [flower](https://github.com/mher/flower) [[文档](https://flower.readthedocs.io/en/latest/)]
- [django-debug-toolbar](https://github.com/django-commons/django-debug-toolbar) [[文档](https://django-debug-toolbar.readthedocs.io/en/latest/index.html)]
- [django-import-export](https://github.com/django-import-export/django-import-export) [[文档](https://django-import-export.readthedocs.io/en/latest/)]
- [django-structlog](https://github.com/jrobichaud/django-structlog) [[文档](https://django-structlog.readthedocs.io/en/latest/)]
    - [structlog](https://github.com/hynek/structlog) [[文档](https://www.structlog.org/en/stable/)]
- [django-rest-framework](https://github.com/encode/django-rest-framework/tree/master) [[文档](https://www.django-rest-framework.org/)]
    - [django-rest-knox](https://github.com/jazzband/django-rest-knox) [[文档](https://jazzband.github.io/django-rest-knox/)]
- [drf-spectacular](https://github.com/tfranzel/drf-spectacular) [[文档](https://drf-spectacular.readthedocs.io/en/latest/)]
- [django-unfold](https://github.com/unfoldadmin/django-unfold) [[文档](https://unfoldadmin.com/docs/)]

## 工具库

- [arrow](https://github.com/arrow-py/arrow) [[文档](https://arrow.readthedocs.io/en/latest/)]
- [more-itertools](https://github.com/more-itertools/more-itertools) [[文档](https://more-itertools.readthedocs.io/en/latest/)]
- [msgspec](https://github.com/jcrist/msgspec) [[文档](https://jcristharif.com/msgspec/)]
- [httpx](https://github.com/encode/httpx/) [[文档](https://www.python-httpx.org/)]
- [tenacity](https://github.com/jd/tenacity) [[文档](https://tenacity.readthedocs.io/en/latest/)]

## Admin

参考

- [官方文档](https://docs.djangoproject.com/zh-hans/5.1/ref/contrib/admin/)
- [Unfold 文档](https://unfoldadmin.com/docs/)

若为非 DEBUG 模式，需要收集静态文件交给 Nginx / Caddy 处理

注意 settings 中的 STATIC_ROOT 配置

```shell
python manage.py collectstatic
```

## Celery

```shell
# 启动 worker
mise run c_worker
# 或指定队列
mise run c_worker -Q celery,priority
# 或
celery -A {{ cookiecutter.project_slug }} worker -l INFO -Q celery -P solo
# 注意 -P solo 为单进程模式，不适用于生产环境
# 生产应不设置（等同于使用 prefork）或 gevent（需要安装）
# -c 设置并发数 例如 -c 2

# 启动 beat
# beat 只需要 1 个实例
mise run c_beat
# 或
celery -A {{ cookiecutter.project_slug }} beat -l INFO

# 启动 flower
mise run c_flower
# or
celery -A {{ cookiecutter.project_slug }} flower --address=127.0.0.1 --url_prefix=admin/flower

# 同时启动 server, beat, worker, flower
mise run all
```

## Oidc 服务配置示例

- Authentik
   - base_url: <your-domain>/application/o/<provider-name-in-authentik>
- Gitlab
   - base_url: <your-domain>
- Casdoor
   - base_url: <your-domain>
   - username 字段 (username_field): name
   - name 字段 (name_field): displayName
