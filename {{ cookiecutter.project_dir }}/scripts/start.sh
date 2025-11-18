#!/bin/bash

APP="{{ cookiecutter.project_slug }}"
SCRIPT_DIR=$(dirname "$0")
BASE_DIR=$(dirname "$SCRIPT_DIR")

# 查找进程PID
pid=$(ps aux | grep "$APP" | grep -v grep | awk '{print $2}')
if [[ -n "$pid" ]]; then
    echo "进程已经在运行中，请先停止进程或使用 restart.sh 重启进程。"
    exit 1
fi

# 启动进程
cd $BASE_DIR
nohup gunicorn -c gunicorn_config.py {{ cookiecutter.project_slug }}.wsgi > nohup.out 2>&1 &

sleep 1  # 等待进程启动
pid=$(ps aux | grep "$APP" | grep -v grep | awk '{print $2}')
if [[ -n "$pid" ]]; then
    echo "进程已成功启动，PID: $pid"
else
    echo "进程启动失败"
    exit 1
fi
