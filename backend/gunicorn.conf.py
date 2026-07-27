"""
Gunicorn 生产配置

用法:
    gunicorn main:app -c gunicorn.conf.py
"""

import multiprocessing

bind = "0.0.0.0:8000"
worker_class = "uvicorn.workers.UvicornWorker"
workers = multiprocessing.cpu_count() * 2 + 1
preload_app = True
max_requests = 1000
max_requests_jitter = 50
timeout = 120
keepalive = 5

# 日志
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"
