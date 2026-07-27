# Axhub Make 重构实施计划

> 基于 PRD，从 React/Node.js 重构为 FastAPI + Vue 架构
> 审批后执行

---

## 一、架构变更总览

### 当前架构 (即将替换)

```
Frontend (React 18 + Excalidraw + Ant Design)
    ↕ HTTP / SSE
Backend (Node.js + TypeScript + Vite)
    ↕ MCP / ACP
AI Runtime (ACP / Direct LLM)
```

### 目标架构

```
+--------------------------------------------------+
|  Desktop (Vue 3 + Naive UI + Tauri)               |
|  ┌──────────────────────────────────────────────┐  |
|  │  画布 (vue-sketch / custom canvas)           │  |
|  │  标注面板                                    │  |
|  │  知识库面板 / 发布面板 / 设置                │  |
|  │  AI 对话面板 (流式 SSE)                      │  |
|  └──────────────────────┬───────────────────────┘  |
+-------------------------|-------------------------+
                          ↕ HTTP/SSE/WebSocket
+-------------------------|-------------------------+
|  Backend (FastAPI + Python 3.11+)                |
|  ┌──────────────────────────────────────────────┐  |
|  │  API Layer (FastAPI routers)                 │  |
|  │  ├── /api/prototypes/*  原型 CRUD            │  |
|  │  ├── /api/annotations/* 标注 CRUD + 版本     │  |
|  │  ├── /api/knowledge/*   知识库               │  |
|  │  ├── /api/publish/*     发布管理             │  |
|  │  └── /api/ai/*          AI 调用 (SSE流式)    │  |
|  ├──────────────────────────────────────────────┤  |
|  │  AI Engine (OpenAI SDK + LangGraph)          │  |
|  │  ├── LLM 调用层 (OpenAI-compatible)           │  |
|  │  ├── Agent 工作流 (LangGraph)                 │  |
|  │  │   ├── 原型生成 Agent                       │  |
|  │  │   ├── 标注执行 Agent                       │  |
|  │  │   ├── 知识抽取 Agent                       │  |
|  │  │   └── 审查 Agent                          │  |
|  │  └── 流式响应 (SSE)                           │  |
|  ├──────────────────────────────────────────────┤  |
|  │  Data Layer                                   │  |
|  │  ├── SQLite (本地开发) / PostgreSQL (生产)     │  |
|  │  ├── 文件存储 (原型文件/素材)                  │  |
|  │  └── 向量存储 (pgvector / Chroma)             │  |
|  └──────────────────────────────────────────────┘  |
+--------------------------------------------------+
```

---

## 二、阶段划分与工期估算

**总工期：12-16 周（1-2 人全职）**

### 阶段一：基础设施与数据层（2-3 周）

| 任务 | 产出 | 工时 |
|------|------|------|
| 1.1 FastAPI 项目骨架 | 项目结构、配置管理、依赖管理 | 2天 |
| 1.2 数据库模型定义 | SQLAlchemy models for 原型/标注/知识库/发布 | 3天 |
| 1.3 数据库迁移 | Alembic 初始化 + 初始迁移 | 1天 |
| 1.4 文件存储服务 | 原型文件/素材/导出包存储 | 2天 |
| 1.5 Docker / 开发环境 | docker-compose + 开发脚本 | 2天 |
| 1.6 认证基础 | API Key / JWT 认证中间件 | 2天 |

### 阶段二：核心 API 迁移（3-4 周）

| 任务 | 产出 | 工时 |
|------|------|------|
| 2.1 原型 API | CRUD + 导出 (HTML/Axure/Figma) | 5天 |
| 2.2 标注 API | CRUD + 版本管理 (保留现有 annotation-source.json 兼容) | 5天 |
| 2.3 知识库 API | CRUD + 搜索 (迁移现有实现) | 3天 |
| 2.4 发布 API | 通道管理 + 部署记录 | 3天 |
| 2.5 AI 上下文 API | Context Bundle + Prompt Pack | 3天 |
| 2.6 数据迁移工具 | 从现有 .json 文件导入 | 2天 |

### 阶段三：AI 引擎（3-4 周）

| 任务 | 产出 | 工时 |
|------|------|------|
| 3.1 LLM 调用层 | OpenAI SDK 封装 + 重试/退避/流式 | 3天 |
| 3.2 模型路由 | 简单/中等/复杂 三级路由 | 2天 |
| 3.3 原型生成 Agent | LangGraph 工作流：需求→布局→代码 | 5天 |
| 3.4 标注执行 Agent | LangGraph 工作流：分析→执行→验证 | 3天 |
| 3.5 知识抽取 Agent | 自动抽取+去重+入库 | 3天 |
| 3.6 审查 Agent | 多维度审查 (功能/安全/UX) | 3天 |
| 3.7 SSE 流式响应 | Server-Sent Events 统一出口 | 2天 |

### 阶段四：Vue 前端基础（2-3 周）

| 任务 | 产出 | 工时 |
|------|------|------|
| 4.1 Vue 项目骨架 | Vite + Vue 3 + Naive UI + Pinia + Vue Router | 2天 |
| 4.2 布局与导航 | 侧边栏 + 顶部栏 + 内容区 | 2天 |
| 4.3 API 客户端 | 基于 fetch/axios 的类型安全客户端生成 | 3天 |
| 4.4 状态管理 | Pinia stores (原型/标注/知识库/发布/AI) | 3天 |
| 4.5 路由与页面结构 | 所有页面的路由框架 + 骨架屏 | 2天 |
| 4.6 暗色主题 | Naive UI dark mode 配置 | 1天 |

### 阶段五：Vue 功能页面（3-4 周）

| 任务 | 产出 | 工时 |
|------|------|------|
| 5.1 画布页面 | 画布容器 + 工具条 + 元素面板 | 5天 |
| 5.2 标注系统页面 | 标注列表 + 编辑器 + 版本时间轴 | 5天 |
| 5.3 知识库页面 | 条目列表 + 搜索 + 编辑器 | 3天 |
| 5.4 发布管理页面 | 通道卡片 + 部署记录 + 仪表盘 | 3天 |
| 5.5 AI 对话面板 | 流式对话 + 上下文管理 + 历史 | 5天 |
| 5.6 设置页面 | 项目设置 + AI 配置 + 账号 | 2天 |
| 5.7 项目仪表盘 | 总览统计 + 最近活动 | 2天 |

### 阶段六：桌面端打包（1-2 周）

| 任务 | 产出 | 工时 |
|------|------|------|
| 6.1 Tauri 集成 | Rust 层配置 + 窗口管理 + 系统托盘 | 3天 |
| 6.2 本地文件系统 | 拖拽导入 + 本地项目存储 | 2天 |
| 6.3 自动更新 | Tauri updater 配置 | 2天 |
| 6.4 构建与分发 | Windows/macOS/Linux 构建脚本 | 2天 |

---

## 三、技术选型明细

### 后端 (Python)

| 组件 | 选型 | 理由 |
|------|------|------|
| Web 框架 | FastAPI | 异步支持、自动 OpenAPI docs、Pydantic 验证 |
| ORM | SQLAlchemy 2.0 + Alembic | 成熟、支持异步、迁移管理 |
| 数据库 | SQLite (dev) / PostgreSQL (prod) | 本地开发零配置、生产可扩展 |
| AI SDK | openai >= 1.0 | OpenAI 兼容 API 统一接口 |
| Agent 框架 | LangGraph | 有状态图、流式输出、分支/循环 |
| 向量存储 | Chroma (dev) / pgvector (prod) | 语义搜索 |
| 异步任务 | FastAPI BackgroundTasks + asyncio | 简单可靠 |
| 配置管理 | pydantic-settings | 环境变量 + .env |
| 测试 | pytest + httpx | FastAPI 官方推荐 |

### 前端 (Vue)

| 组件 | 选型 | 理由 |
|------|------|------|
| 框架 | Vue 3.4+ (Composition API) | 响应式、TypeScript 友好 |
| UI 库 | Naive UI | 组件丰富、按需加载、TypeScript 原生 |
| 构建 | Vite | 快速 HMR |
| 状态管理 | Pinia | Vue 官方推荐 |
| 路由 | Vue Router 4 | SPA 路由 |
| 画布 (待定) | HTML Canvas + 自研 / vue-sketch | 需评估 |
| 桌面壳 | Tauri 2.0 | 轻量、跨平台、Rust 安全 |
| HTTP 客户端 | ofetch / @vueuse/core | Naive UI 生态 |
| 流式 SSE | EventSource + 自定义 hook | 原生支持 |

### 关键决策点

| 决策 | 选项 | 建议 | 理由 |
|------|------|------|------|
| **画布方案** | 1) 自研 Canvas 2) Excalidraw 适配 3) 其它 | ⏳ **需讨论** | Excalidraw 是 React 组件，Vue 中复用需 WebComponent 包装或 iframe |
| **数据库** | SQLite vs PostgreSQL | SQLite 起步 | 本地优先，PostgreSQL 后续加 |
| **是否有存量兼容需求** | 1) 完整重写 2) 逐步替换 | ⏳ **需讨论** | 影响阶段二的数据迁移工作量 |
| **桌面端优先级** | 1) 先 Web 再 Tauri 2) 一步到位 | ⏳ **需讨论** | Tauri 配置需 Rust 环境 |

---

## 四、后端目录结构（建议）

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── config.py               # pydantic-settings 配置
│   ├── database.py             # SQLAlchemy 引擎 + session
│   │
│   ├── models/                 # SQLAlchemy ORM 模型
│   │   ├── __init__.py
│   │   ├── prototype.py
│   │   ├── annotation.py
│   │   ├── knowledge.py
│   │   └── publish.py
│   │
│   ├── schemas/                # Pydantic 请求/响应模型
│   │   ├── __init__.py
│   │   ├── prototype.py
│   │   ├── annotation.py
│   │   ├── knowledge.py
│   │   └── publish.py
│   │
│   ├── routers/                # FastAPI 路由
│   │   ├── __init__.py
│   │   ├── prototypes.py
│   │   ├── annotations.py
│   │   ├── knowledge.py
│   │   ├── publish.py
│   │   └── ai.py
│   │
│   ├── services/               # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── annotation_service.py
│   │   ├── knowledge_service.py
│   │   ├── publish_service.py
│   │   └── export_service.py
│   │
│   ├── ai/                     # AI 引擎
│   │   ├── __init__.py
│   │   ├── llm.py              # OpenAI SDK 封装
│   │   ├── router.py           # 模型路由
│   │   ├── agents/             # LangGraph Agents
│   │   │   ├── __init__.py
│   │   │   ├── prototype_agent.py
│   │   │   ├── annotation_agent.py
│   │   │   ├── knowledge_agent.py
│   │   │   └── review_agent.py
│   │   └── prompts/            # System Prompts
│   │       ├── __init__.py
│   │       ├── prototype.yaml
│   │       ├── annotation.yaml
│   │       └── review.yaml
│   │
│   └── utils/                  # 工具函数
│       ├── __init__.py
│       ├── file_storage.py
│       └── sse.py              # SSE 流式响应工具
│
├── migrations/                 # Alembic
│   ├── env.py
│   └── versions/
│
├── tests/
│   ├── conftest.py
│   ├── test_annotations.py
│   ├── test_knowledge.py
│   ├── test_publish.py
│   └── test_ai.py
│
├── data/                       # 本地文件存储 (gitignore)
├── .env.example
├── pyproject.toml
├── requirements.txt
└── Dockerfile
```

---

## 五、前端目录结构（建议）

```
frontend/
├── src/
│   ├── main.ts                 # Vue 应用入口
│   ├── App.vue                 # 根组件
│   │
│   ├── layouts/                # 布局组件
│   │   ├── MainLayout.vue      # 主布局 (侧边栏 + 内容)
│   │   └── AuthLayout.vue      # 登录/注册布局
│   │
│   ├── pages/                  # 页面组件
│   │   ├── dashboard/
│   │   │   └── index.vue       # 仪表盘
│   │   ├── prototypes/
│   │   │   ├── index.vue       # 原型列表
│   │   │   ├── [id]/           # 原型编辑
│   │   │   │   ├── canvas.vue  # 画布
│   │   │   │   └── annotations.vue  # 标注面板
│   │   │   └── new.vue         # 新建原型
│   │   ├── knowledge/
│   │   │   └── index.vue       # 知识库
│   │   ├── publish/
│   │   │   └── index.vue       # 发布管理
│   │   ├── settings/
│   │   │   └── index.vue       # 设置
│   │   └── ai/
│   │       └── chat.vue        # AI 对话
│   │
│   ├── components/             # 可复用组件
│   │   ├── common/
│   │   │   ├── PageHeader.vue
│   │   │   └── EmptyState.vue
│   │   ├── annotation/
│   │   │   ├── AnnotationBadge.vue
│   │   │   ├── AnnotationEditor.vue
│   │   │   └── VersionTimeline.vue
│   │   ├── knowledge/
│   │   │   ├── EntryCard.vue
│   │   │   └── EntryEditor.vue
│   │   ├── publish/
│   │   │   ├── ChannelCard.vue
│   │   │   └── DeployHistory.vue
│   │   └── ai/
│   │       ├── ChatMessage.vue
│   │       └── ChatInput.vue
│   │
│   ├── composables/            # 可组合函数 (hooks)
│   │   ├── useApi.ts
│   │   ├── useStreamSSE.ts
│   │   ├── useAnnotation.ts
│   │   ├── useKnowledge.ts
│   │   └── usePublish.ts
│   │
│   ├── stores/                 # Pinia 状态
│   │   ├── prototype.ts
│   │   ├── annotation.ts
│   │   ├── knowledge.ts
│   │   ├── publish.ts
│   │   ├── ai.ts
│   │   └── app.ts
│   │
│   ├── api/                    # API 客户端
│   │   ├── client.ts           # ofetch 实例
│   │   ├── prototypes.ts
│   │   ├── annotations.ts
│   │   ├── knowledge.ts
│   │   ├── publish.ts
│   │   └── ai.ts
│   │
│   ├── types/                  # TypeScript 类型
│   │   ├── prototype.ts
│   │   ├── annotation.ts
│   │   ├── knowledge.ts
│   │   ├── publish.ts
│   │   └── ai.ts
│   │
│   └── utils/
│       ├── format.ts
│       └── constants.ts
│
├── src-tauri/                  # Tauri Rust 层
│   ├── Cargo.toml
│   ├── src/
│   │   └── main.rs
│   └── tauri.conf.json
│
├── public/
├── index.html
├── vite.config.ts
├── tsconfig.json
├── package.json
└── tailwind.config.ts (可选)
```

---

## 六、数据库模型（核心）

### 6.1 原型 (prototype)

```python
class Prototype(Base):
    __tablename__ = "prototypes"
    id: str = Column(String, primary_key=True)
    name: str = Column(String, nullable=False)
    description: str = Column(Text, default="")
    page_id: str = Column(String, default="")
    canvas_data: dict = Column(JSON, default=dict)  # Excalidraw 数据
    created_at: datetime = Column(DateTime, default=func.now())
    updated_at: datetime = Column(DateTime, default=func.now(), onupdate=func.now())
```

### 6.2 标注 (annotation)

```python
class Annotation(Base):
    __tablename__ = "annotations"
    id: str = Column(String, primary_key=True)
    prototype_id: str = Column(String, ForeignKey("prototypes.id"))
    title: str = Column(String, default="")
    annotation_text: str = Column(Text, default="")
    markdown: str = Column(Text, default="")
    color: str = Column(String, default="#1677FF")
    scope: str = Column(String, default="element")  # element | page
    locator: dict = Column(JSON, default=dict)  # CSS selector / fingerprint
    page_id: str = Column(String, default="")
    status: str = Column(String, default="active")
    created_at: datetime = Column(DateTime, default=func.now())
    updated_at: datetime = Column(DateTime, default=func.now(), onupdate=func.now())
```

### 6.3 版本 (version)

```python
class AnnotationVersion(Base):
    __tablename__ = "annotation_versions"
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    prototype_id: str = Column(String, ForeignKey("prototypes.id"))
    version: int = Column(Integer, nullable=False)
    diff: list = Column(JSON, default=list)
    summary: str = Column(String, default="")
    tags: list = Column(JSON, default=list)
    status: str = Column(String, default="draft")
    created_at: datetime = Column(DateTime, default=func.now())
```

### 6.4 知识条目 (knowledge_entry)

```python
class KnowledgeEntry(Base):
    __tablename__ = "knowledge_entries"
    id: str = Column(String, primary_key=True)
    type: str = Column(String, nullable=False)  # term|decision|constraint|feedback|rule
    title: str = Column(String, nullable=False)
    content: str = Column(Text, nullable=False)
    tags: list = Column(JSON, default=list)
    source: str = Column(String, default="")
    created_at: datetime = Column(DateTime, default=func.now())
    updated_at: datetime = Column(DateTime, default=func.now(), onupdate=func.now())
```

---

## 七、AI 引擎设计

### 7.1 LLM 调用层

```python
from openai import AsyncOpenAI
from pydantic_settings import BaseSettings

class AIConfig(BaseSettings):
    api_key: str = ""
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o"
    # 模型路由配置
    simple_model: str = "gpt-4o-mini"
    medium_model: str = "gpt-4o"
    complex_model: str = "o3-mini"

class LLMService:
    def __init__(self, config: AIConfig):
        self.client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
        )
        self.config = config

    async def chat_stream(
        self, messages: list, model: str | None = None
    ) -> AsyncIterator[str]:
        response = await self.client.chat.completions.create(
            model=model or self.config.model,
            messages=messages,
            stream=True,
        )
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def chat(self, messages: list, model: str | None = None) -> str:
        response = await self.client.chat.completions.create(
            model=model or self.config.model,
            messages=messages,
        )
        return response.choices[0].message.content or ""
```

### 7.2 LangGraph Agent — 标注执行示例

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal

class AnnotationState(TypedDict):
    prompt: str
    element_info: dict
    analysis: str
    plan: list[str]
    result: str
    verified: bool

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
        builder.add_conditional_edges(
            "verify",
            self._decide_next,
            {"accepted": END, "retry": "execute"},
        )
        builder.add_edge("analyze", "plan")
        builder.add_edge("plan", "execute")
        builder.add_edge("execute", "verify")
        return builder.compile()

    async def _analyze(self, state: AnnotationState) -> dict:
        # 分析用户需求和元素信息
        ...

    async def _plan(self, state: AnnotationState) -> dict:
        # 制定修改计划
        ...

    async def _execute(self, state: AnnotationState) -> dict:
        # 执行修改
        ...

    async def _verify(self, state: AnnotationState) -> dict:
        # 验证结果
        ...

    def _decide_next(self, state: AnnotationState) -> Literal["accepted", "retry"]:
        return "accepted" if state["verified"] else "retry"

    async def run(self, prompt: str, element_info: dict) -> AsyncIterator[str]:
        # 流式执行 Agent 并产出结果
        ...
```

---

## 八、需要你确认的决策点

以下是在开始实施前需要你决定的：

| # | 决策 | 选项 | 建议 | 
|---|------|------|------|
| **D1** | **画布方案** | A) 用 HTML Canvas 自研轻量画布<br>B) iframe 嵌入 Excalidraw (复用现有)<br>C) 找 Vue 生态的画布库 | **已确认 B** —— iframe 嵌入现有 Excalidraw，快速复用标注功能 |
| **D2** | **重写策略** | A) 完整重写：全部代码用 Python/Vue 重写<br>B) 渐进替换：后端先迁 Python，前端逐步替换 | **已确认 B** —— 渐进替换，后端先行 |
| **D3** | **桌面端优先 vs Web 优先** | A) 先做 Web (Vite dev server)，再加 Tauri 壳<br>B) 一步到位 Tauri | **已确认 A** —— Web 优先，Tauri 后期加壳 |
| **D4** | **存量数据兼容** | A) 保留现有 annotation-source.json 格式，Python 直接读写<br>B) 迁移到 SQL，写导入工具 | **已确认 B** —— 直接建 SQL 表 + 导入工具 |
| **D5** | **AI Config 读取来源** | A) 服务端 .env 配置<br>B) 前端 localStorage 配置 (现有方式) | **已确认 A** —— 服务端 .env，API Key 不暴露给浏览器 |

---

## 九、风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| Excalidraw 在 Vue 中复用困难 | 中 | 高 | iframe 嵌入是最小成本方案 |
| Python 异步 + LangGraph 学习曲线 | 中 | 中 | FastAPI 异步支持成熟，LangGraph 文档完善 |
| 过渡期双栈维护成本 | 高 | 中 | 渐进替换策略，明确边界 |
| 原 Node.js 中的 Vite on-demand build 逻辑复杂 | 中 | 高 | 原型构建可用 Python subprocess 调用 npm |
| Tauri 打包环境 (Rust) 配置 | 低 | 中 | 后期实施，有完善的文档 |

---

*计划制定人: Reasonix*
*请审批后开始实施第一阶段。*
