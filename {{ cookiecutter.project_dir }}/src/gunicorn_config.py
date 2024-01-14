import multiprocessing

bind = '127.0.0.1:15701'  # 指定 Django 应用的 IP 地址和端口号
workers = {{ cookiecutter.gunicorn_workers_num }}  # 设置工作进程的数量
timeout = {{ cookiecutter.gunicorn_timeout }}  # 请求超时时间

# 获取cpu核心数
