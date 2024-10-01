# {{ cookiecutter.project_name|trim() }}


## simple-ui admin

若为非 DEBUG 模式，需要收集静态文件交给 Nginx / Caddy 处理

注意 settings 中的 STATIC_ROOT 配置

```shell
python manage.py collectstatic
```
