# Axhub Make Backend

FastAPI + Tortoise ORM + OpenAI SDK + LangGraph

## 环境要求

- [uv](https://docs.astral.sh/uv/) (包管理器) — 安装：`pip install uv` 或官方脚本
- Python 3.11+（推荐 3.12，本机已有 3.12.8）

## 开发（推荐 uv 工作流）

```bash
cd backend

# 1. 创建虚拟环境并安装依赖（首次）
#    uv 自动创建 .venv 并锁定版本到 uv.lock
uv sync --python 3.12 --extra dev

# 2. 启动开发服务器（.venv 内的 uvicorn）
uv run uvicorn main:app --reload --port 8000

# 3. 运行测试（dev 依赖：pytest / pytest-asyncio / ruff / mypy）
uv run pytest tests/

# 4. 代码检查
uv run ruff check .
uv run mypy .

# 5. 数据库迁移（aerich）
uv run aerich init -t config.tortoise.get_tortoise_config
uv run aerich init-db
```

> **注意**：`--extra dev` 必须带上，否则 pytest/ruff/mypy 不会安装
> （它们声明在 `[project.optional-dependencies] dev` 中）。

## 生产

```bash
cd backend
uv run gunicorn main:app -c gunicorn.conf.py
# 或
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

## 环境变量

复制 `.env.example` 为 `.env` 并填写配置。

| 变量 | 说明 | 默认 |
|------|------|------|
| `DEBUG` | 开发模式（SQLite + /docs） | `true` |
| `DB_HOST/DB_PORT/DB_USER/DB_PASSWORD/DB_NAME` | PostgreSQL（DEBUG=false 时生效） | — |
| `AI_API_KEY` | OpenAI 兼容 API Key | — |
| `AI_BASE_URL` | LLM API 地址 | `https://api.openai.com/v1` |
| `ACCESS_PASSWORD` | 网络访问控制密码 | 空 |
| `DATA_DIR` | 文件/附件存储目录 | `data` |
