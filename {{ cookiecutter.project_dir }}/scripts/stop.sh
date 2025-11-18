#!/bin/bash

APP="{{ cookiecutter.project_slug }}"

# 查找进程PID
pid=$(ps aux | grep "$APP" | grep -v grep | awk '{print $2}')

if [[ -z "$pid" ]]; then
    echo "进程未在运行中"
    exit 1
fi

# 关闭进程
for id in $pid; do
    if kill -9 "$id" >/dev/null 2>&1; then
        echo "关闭进程 $id 成功"
    else
        echo "关闭进程 $id 失败"
        exit 1
    fi
done

echo "stop成功"
