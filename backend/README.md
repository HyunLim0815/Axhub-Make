# Axhub Make Backend

FastAPI + Tortoise ORM + OpenAI SDK + LangGraph

## 开发

```bash
# 安装 UV (包管理器)
pip install uv

# 安装依赖
uv sync

# 启动开发服务器
uvicorn main:app --reload --port 8000

# 数据库迁移
aerich init -t config.tortoise.get_tortoise_config
aerich init-db
```

## 生产

```bash
gunicorn main:app -c gunicorn.conf.py
```

## 环境变量

复制 `.env.example` 为 `.env` 并填写配置。
