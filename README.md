# ClanEver DRF Template

一个简单的 drf 模板。初始化 Django 项目时跳过 `rye init` 和 `django-admin startproject xxx` 等琐碎步骤。

使用 [rye](https://github.com/mitsuhiko/rye) 和 [cookiecutter](https://github.com/cookiecutter/cookiecutter) 工具

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

## 使用方法

1. 安装 [rye](https://github.com/mitsuhiko/rye)

2. 使用 rye 安装 cookiecutter
    ```shell
    rye install cookiecutter --extra-requirement jinja2-strcase --extra-requirement tomlkit
    ```

3. 使用此模板
    ```shell
    cookiecutter https://github.com/ClanEver/clanever-drf-template.git
    ```

4. 更改 settings.py 然后在开发环境中运行
    ```shell
    # 创建迁移并应用迁移
    rye run dev_mnm
    # 运行服务器
    rye run dev
    ```

5. [可选] 使用应用模板
    ```shell
    rye run startapp
    # 或
    cookiecutter https://github.com/ClanEver/clanever-drf-app-template.git
    ```

## 相关

[clanever-drf-app-template](https://github.com/ClanEver/clanever-drf-app-template/)

## 许可证

[MIT](./LICENSE)
