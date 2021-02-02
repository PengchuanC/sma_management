#!/usr/bin/env sh

echo "以asgi形式启动SMA后端服务"

echo "查询已运行的asgi服务"

ps aux|grep uvicorn|grep -v grep|cut -c 9-15|xargs kill -9

nohup uvicorn sma_management.asgi:application --host 0.0.0.0 --port 5000 > asgi.log &
jobs