# Axhub Make — 后端重构规划 (FastAPI 企业级规范)

> 依据 `fastapi-guider` 规范重新设计
> 架构：FastAPI + Tortoise ORM + OpenAI SDK + LangGraph

---

## 目录结构

```
backend/
├── api/
│   ├── controllers/              # 控制器层（业务逻辑）
│   │   ├── PrototypeController.py
│   │   ├── AnnotationController.py
│   │   ├── KnowledgeController.py
│   │   ├── PublishController.py
│   │   └── AIController.py
│   ├── responses/                # 统一响应模型
│   │   ├── Base.py               # ApiResponse, PageResponse
│   │   └── responses_example.py
│   ├── router/v1/                # API 版本路由
│   │   ├── __init__.py           # 聚合所有 router
│   │   ├── prototypes.py
│   │   ├── annotations.py
│   │   ├── knowledge.py
│   │   ├── publish.py
│   │   └── ai.py
│   └── schemas/                  # Pydantic 请求/响应 schema
│       ├── prototype.py
│       ├── annotation.py
│       ├── knowledge.py
│       ├── publish.py
│       └── ai.py
│
├── config/                       # 配置层
│   ├── __init__.py
│   ├── db.py                     # DatabaseSettings (pydantic-settings)
│   └── tortoise.py               # Tortoise ORM 配置
│
├── middlewares/                   # 中间件
│   ├── catch_error.py            # 全局异常捕获
│   ├── token_middlewares.py      # API Key / JWT 认证
│   └── permission_middlewares.py # 权限校验
│
├── models/                       # Tortoise ORM 模型
│   ├── basic_model.py            # BaseModel（软删除、时间戳、基础 CRUD）
│   ├── prototype.py              # 原型模型
│   ├── annotation.py             # 标注 + 版本模型
│   ├── knowledge.py              # 知识条目模型
│   └── publish.py                # 发布通道 + 记录模型
│
├── ai/                           # AI 引擎（单独目录）
│   ├── __init__.py
│   ├── llm.py                    # OpenAI SDK 封装
│   ├── router.py                 # 模型路由
│   ├── agents/
│   │   ├── prototype_agent.py    # 原型生成 Agent
│   │   ├── annotation_agent.py   # 标注执行 Agent
│   │   ├── knowledge_agent.py    # 知识抽取 Agent
│   │   └── review_agent.py       # 审查 Agent
│   └── prompts/
│       ├── prototype.yaml
│       ├── annotation.yaml
│       └── review.yaml
│
├── utils/                        # 工具层
│   ├── __init__.py
│   ├── auth/security.py          # API Key 认证
│   ├── depends/                  # FastAPI 依赖
│   │   ├── auth.py               # 认证依赖
│   │   └── pagination.py         # 分页依赖
│   ├── Enums/                    # 枚举
│   │   ├── __init__.py
│   │   └── annotation.py
│   └── tools/                    # 工具函数
│       ├── logger.py             # Loguru 配置
│       ├── cache.py              # Redis 缓存装饰器
│       └── sse.py                # SSE 流式响应工具
│
├── tests/                        # 测试
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   │   ├── test_annotations.py
│   │   ├── test_knowledge.py
│   │   └── test_publish.py
│   └── e2e/
│       └── test_full_flow.py
│
├── main.py                       # FastAPI 应用入口
├── gunicorn.conf.py              # Gunicorn 生产配置
├── .env.example
├── pyproject.toml
├── Dockerfile
└── docker-compose.yml
```

---

## 技术栈明细

| 组件 | 选型 | 用途 |
|------|------|------|
| **Web 框架** | FastAPI >=0.115.6 | 异步 API |
| **ORM** | Tortoise ORM >=0.25.0 + asyncpg >=0.30.0 | 数据库操作 |
| **数据库** | PostgreSQL 16 | 持久化存储 |
| **数据验证** | Pydantic (FastAPI 内置) | 请求/响应校验 |
| **配置管理** | pydantic-settings >=2.14.2 | .env → 环境变量 |
| **缓存** | Redis (redis[hiredis] >=5.2.1) | 会话/缓存 |
| **日志** | Loguru >=0.7.3 + structlog | 结构化日志 |
| **任务调度** | APScheduler >=3.11.3 | 定时任务 |
| **监控** | prometheus-fastapi-instrumentator >=7.1.0 | Prometheus 指标 |
| **错误追踪** | Sentry SDK >=2.66.1 | 异常监控 |
| **限流** | SlowAPI >=0.1.10 | API 限流 |
| **序列化** | orjson >=3.11.9 | 高性能 JSON |
| **安全头** | secure >=2.0.1 | HTTP 安全头 |
| **ASGI 服务器** | Uvicorn >=0.34.0 | 开发运行 |
| **进程管理** | Gunicorn >=23.0.0 | 生产运行 |
| **请求追踪** | asgi-correlation-id >=5.0.1 | 请求链路 ID |
| **包管理** | UV | 依赖管理 |
| **AI SDK** | openai >=1.0 | LLM 调用 |
| **Agent** | langgraph | Agent 工作流 |

---

## 阶段划分

### 阶段一：基础设施与数据层（2-3 周）

| # | 任务 | 产出 | 工时 |
|---|------|------|------|
| 1.1 | **项目骨架** | `main.py` + `pyproject.toml` + `.env.example` + 目录结构 | 1天 |
| 1.2 | **配置管理** | `config/db.py` (pydantic-settings) + `config/tortoise.py` | 1天 |
| 1.3 | **日志配置** | `utils/tools/logger.py` (Loguru + structlog) | 0.5天 |
| 1.4 | **基础模型** | `models/basic_model.py` (BaseModel: 软删除/时间戳/基础 CRUD) | 1天 |
| 1.5 | **领域模型** | 4 张核心表：prototype / annotation / knowledge / publish | 3天 |
| 1.6 | **统一响应** | `api/responses/Base.py` (ApiResponse / PageResponse) | 0.5天 |
| 1.7 | **异常处理** | `middlewares/catch_error.py` (全局异常捕获) | 1天 |
| 1.8 | **认证中间件** | `middlewares/token_middlewares.py` (API Key) | 1天 |
| 1.9 | **限流 + 安全头** | SlowAPI + secure 配置 | 0.5天 |
| 1.10 | **监控 + 追踪** | Prometheus + Sentry + asgi-correlation-id | 1天 |
| 1.11 | **健康检查** | `GET /health` + `GET /health/detailed` | 0.5天 |
| 1.12 | **Docker 环境** | `docker-compose.yml` (app + postgres + redis) + `Dockerfile` | 2天 |

### 阶段二：核心 API（3-4 周）

按 skill 规范，每张表都遵循 RESTful 模式：

```python
router = APIRouter(prefix="/v1/prototypes", tags=["prototypes"])
# GET    /{id}   获取单个
# GET    /       列表（分页）
# POST   /       创建
# PUT    /{id}   全量更新
# PATCH  /{id}   部分更新
# DELETE/{id}   删除
```

| # | 任务 | API 路由 | 工时 |
|---|------|---------|------|
| 2.1 | **原型 API** | `/v1/prototypes/*` + 导出 endpoints | 4天 |
| 2.2 | **标注 API** | `/v1/annotations/*` + 版本管理 | 5天 |
| 2.3 | **知识库 API** | `/v1/knowledge/*` + 搜索 | 3天 |
| 2.4 | **发布 API** | `/v1/publish/*` + 部署 | 3天 |
| 2.5 | **AI 上下文 API** | `/v1/ai/context` + `/v1/ai/bundle` | 3天 |
| 2.6 | **数据迁移工具** | 从现有 JSON 导入 PostgreSQL | 2天 |
| 2.7 | **API 文档** | FastAPI 自动生成 OpenAPI + 手动补充 | 1天 |

#### 统一响应格式

```python
class ApiResponse(BaseModel):
    code: int = Field(200, description="状态码")
    message: str = Field("success", description="响应消息")
    data: Optional[dict | list] = None

class PageParams(BaseModel):
    page: int = Field(1, ge=1)
    size: int = Field(10, gt=0, le=200)

class PageResponse(BaseModel, Generic[T]):
    data: list[T]
    total: int
    current_page: int
    last_page: int
    per_page: int
```

### 阶段三：AI 引擎（3-4 周）

#### LLM 调用层

```python
# ai/llm.py
import structlog
from openai import AsyncOpenAI

LOGGER = structlog.get_logger(__name__)

class LLMService:
    def __init__(self, config: AIConfig):
        self.client = AsyncOpenAI(
            api_key=config.API_KEY,
            base_url=config.BASE_URL,
        )
        LOGGER.bind(provider=config.PROVIDER).info("LLM service initialized")

    async def chat_stream(
        self, messages: list, model: str = "gpt-4o"
    ) -> AsyncIterator[str]:
        """流式调用，返回 token 迭代器"""
        response = await self.client.chat.completions.create(
            model=model, messages=messages, stream=True
        )
        async for chunk in response:
            if token := chunk.choices[0].delta.content:
                yield token

    async def chat(
        self, messages: list, model: str = "gpt-4o"
    ) -> str:
        """一次性调用，返回完整文本"""
        response = await self.client.chat.completions.create(
            model=model, messages=messages
        )
        return response.choices[0].message.content or ""
```

#### 模型路由

```python
# ai/router.py
class ModelRouter:
    """三级模型路由：成本与能力的平衡"""
    
    SIMPLE_MODEL = "gpt-4o-mini"   # 分类/摘要/简单问答
    MEDIUM_MODEL = "gpt-4o"         # 标准对话/内容生成
    COMPLEX_MODEL = "o3-mini"       # 多步推理/代码/数学

    async def route(self, task: str, context: dict) -> str:
        complexity = await self._assess_complexity(task, context)
        if complexity == "simple":
            return self.SIMPLE_MODEL
        elif complexity == "complex":
            return self.COMPLEX_MODEL
        return self.MEDIUM_MODEL
```

#### LangGraph Agent — 标注执行

```python
# ai/agents/annotation_agent.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal
import structlog

LOGGER = structlog.get_logger(__name__)

class AnnotationState(TypedDict):
    prompt: str
    element_info: dict
    analysis: str
    plan: list[str]
    result: str
    verified: bool
    retry_count: int

MAX_RETRY = 3

class AnnotationAgent:
    def __init__(self, llm: LLMService):
        self.llm = llm
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        builder = StateGraph(AnnotationState)
        builder.add_node("analyze", self._analyze)
        builder.add_node("plan", self._plan)
        builder.add_node("execute", self._execute)
        builder.add_node("verify", self._verify)
        builder.set_entry_point("analyze")
        builder.add_edge("analyze", "plan")
        builder.add_edge("plan", "execute")
        builder.add_edge("execute", "verify")
        builder.add_conditional_edges(
            "verify", self._decide_next,
            {"accepted": END, "retry": "execute", "abort": END},
        )
        return builder.compile()

    async def _analyze(self, state: AnnotationState) -> dict:
        LOGGER.bind(prompt=state["prompt"][:50]).info("Analyzing annotation request")
        # 调用 LLM 分析用户需求和元素上下文
        ...

    async def _decide_next(
        self, state: AnnotationState
    ) -> Literal["accepted", "retry", "abort"]:
        if state["verified"]:
            return "accepted"
        if state["retry_count"] >= MAX_RETRY:
            LOGGER.warning("Max retry reached for annotation")
            return "abort"
        return "retry"
```

### 阶段四：Redis 缓存层（1 周，并行）

| # | 任务 | 产出 | 工时 |
|---|------|------|------|
| 4.1 | 缓存连接池 | `utils/tools/cache.py` (Redis 连接池 + orjson 序列化) | 1天 |
| 4.2 | 缓存装饰器 | `@cached(expire=300, prefix="prototype")` | 1天 |
| 4.3 | 标注缓存 | 标注列表缓存 + 版本列表缓存 | 1天 |
| 4.4 | 知识库缓存 | 搜索缓存 + 热门条目缓存 | 1天 |
| 4.5 | 会话管理 | API Key → Redis 会话 | 1天 |

---

## 数据模型规范

遵循 Tortoise ORM 规范：

### 基础模型

```python
# models/basic_model.py
from tortoise.models import Model
from tortoise import fields

class BaseModel(Model):
    id = fields.IntField(pk=True, auto_increment=True)
    create_time = fields.DatetimeField(auto_now_add=True)
    update_time = fields.DatetimeField(auto_now=True)
    delete_time = fields.DatetimeField(null=True)

    class Meta:
        abstract = True
        ordering = ["-id"]

    async def soft_delete(self) -> None:
        self.delete_time = datetime.now()
        await self.save(update_fields=["delete_time"])

    @classmethod
    async def get_active(cls, **kwargs):
        return await cls.filter(delete_time=None, **kwargs).first()

    @classmethod
    async def get_by_id(cls, id_: int):
        return await cls.filter(id=id_, delete_time=None).first()
```

### 原型模型

```python
# models/prototype.py
from tortoise import fields
from models.basic_model import BaseModel

class Prototype(BaseModel):
    name = fields.CharField(max_length=255)
    description = fields.TextField(default="")
    page_id = fields.CharField(max_length=255, default="")
    canvas_data = fields.JSONField(default=dict)

    class Meta:
        table = "prototypes"
```

### 标注模型

```python
class Annotation(BaseModel):
    prototype = fields.ForeignKeyField("models.Prototype", related_name="annotations")
    title = fields.CharField(max_length=255, default="")
    annotation_text = fields.TextField(default="")
    markdown = fields.TextField(default="")
    color = fields.CharField(max_length=32, default="#1677FF")
    scope = fields.CharField(max_length=16, default="element")  # element | page
    locator = fields.JSONField(default=dict)
    page_id = fields.CharField(max_length=255, default="")
    status = fields.CharField(max_length=32, default="active")

    class Meta:
        table = "annotations"
```

### 版本模型

```python
class AnnotationVersion(BaseModel):
    prototype = fields.ForeignKeyField("models.Prototype", related_name="versions")
    version = fields.IntField()
    diff = fields.JSONField(default=list)
    summary = fields.CharField(max_length=512, default="")
    tags = fields.JSONField(default=list)
    status = fields.CharField(max_length=32, default="draft")

    class Meta:
        table = "annotation_versions"
        ordering = ["-version"]
```

---

## 实施顺序（共 3 个阶段 + 1 并行阶段）

```
第 1-2 周: 阶段一 — 基础设施
  ├── 项目骨架 + 配置 + 日志 + 基础模型
  ├── PostgreSQL + Tortoise ORM 初始化
  ├── Redis 连接 + 缓存基础
  ├── Prometheus + Sentry + 健康检查
  └── Docker Compose (app + postgres + redis)

第 3-6 周: 阶段二 — 核心 API
  ├── 原型 Controller + Router + Schema
  ├── 标注 Controller + 版本管理
  ├── 知识库 Controller + 搜索
  ├── 发布 Controller + 部署
  └── 数据迁移工具

第 4 周并行: 阶段四 — Redis 缓存
  ├── 缓存装饰器
  └── 各模块缓存接入

第 7-10 周: 阶段三 — AI 引擎
  ├── LLMService (OpenAI SDK)
  ├── ModelRouter (三级路由)
  ├── 4 个 LangGraph Agents
  ├── SSE 流式出口
  └── 集成测试
```

---

## 配置示例 (.env)

```env
# 应用
APP_NAME=axhub-make
APP_VERSION=2.0.0
DEBUG=true

# 数据库 (PostgreSQL)
DB_HOST=localhost
DB_PORT=5432
DB_USER=axhub
DB_PASSWORD=axhub_secret
DB_NAME=axhub_make

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# AI
AI_API_KEY=sk-...
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4o
AI_SIMPLE_MODEL=gpt-4o-mini
AI_COMPLEX_MODEL=o3-mini

# 监控
SENTRY_DSN=
PROMETHEUS_ENABLED=true

# 安全
API_KEY=your-api-key-here
CORS_ORIGINS=*
```

---

## 与旧有前端的关系

| 策略 | 说明 |
|------|------|
| **ifram 画布** | 现有 React Excalidraw 编译为独立 HTML，通过 iframe 嵌入 Vue |
| **Vue 前端** | 调 FastAPI 后端，不调 Node.js 服务 |
| **渐进替换** | 先跑通 FastAPI + Vue 最小链路，再逐个迁移功能 |
| **数据迁移** | 从 `annotation-source.json` / `.axhub/knowledge-base.json` 等导入 PostgreSQL |

---

## 测试策略

```bash
# 运行全部测试
pytest

# 单元测试 (模型层)
pytest tests/unit/

# 集成测试 (API)
pytest tests/integration/

# 端到端
pytest tests/e2e/

# 带覆盖率
pytest --cov=api --cov=models --cov=ai --cov-report=term-missing
```

### 测试配置

```python
# tests/conftest.py
@pytest.fixture(scope="session")
def event_loop():
    """session 级事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def initialize_db():
    """使用 sqlite:memory 进行测试"""
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"models": ["models.prototype", "models.annotation", ...]}
    )
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()

@pytest.fixture
async def client():
    """httpx 异步客户端"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
```
