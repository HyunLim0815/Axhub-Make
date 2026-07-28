# Axhub Make — 产品需求文档 (PRD)

> **版本**: 2.0 | **状态**: 迭代中 | **最后更新**: 2026-07-28

---

## 一、产品定位与愿景

### 1.1 一句话定位

Axhub Make 是一个**以项目为核心**的 AI 产品工作流平台，覆盖**需求分析 → 原型生成 → 标注评审 → 知识沉淀 → 发布交付**全链路。

### 1.2 目标用户

| 角色 | 核心痛点 | 使用场景 |
|------|---------|---------|
| **产品经理** | 原型画了、需求写了、评审过了，但交付物散落在各工具中 | 从需求到交付的一站式工作台 |
| **设计师** | 产品经理给的线框图太粗糙，需要重新画视觉稿 | 用 OpenPencil 从线框图生成 UI 精稿 |
| **开发者** | PRD 和原型对不上，需求变更没记录 | 查看标注和版本历史，理解需求上下文 |
| **AI Agent** | 需要结构化上下文才能理解项目 | Context Bundle + 知识库注入 |

### 1.3 产品公式

```
产品价值 = (原型效率 × 标注准确率 × 知识复用率) ÷ 交付摩擦
```

---

## 二、功能全景

### 2.1 项目管理（新增核心模型）

| 功能 | 说明 | 优先级 | 状态 |
|------|------|--------|------|
| **项目 CRUD** | 创建/编辑/删除项目 | P0 | ✅ 已实现 |
| **项目内原型** | 每个项目包含多个原型 | P0 | ✅ 已实现 |
| **项目知识库** | 每个项目有独立的知识条目 | P0 | ✅ 已实现 |
| **团队知识库** | 跨项目共享的团队知识 | P1 | ✅ 已实现 |
| 项目仪表盘 | 项目级统计和状态总览 | P1 | ⏳ 待完善 |

### 2.2 原型管理

| 功能 | 说明 | 状态 |
|------|------|------|
| 画布编辑 | Excalidraw 自由绘制 | 已有 |
| AI 生成原型 | Prompt → 页面结构 | 已有 |
| 设备外壳 | 手机/平板/桌面预览 | 已有 |
| **项目关联** | 原型属于特定项目 | ✅ 新增 |
| 多页面管理 | 同一原型多个页面 | 已有 |

### 2.3 标注系统

| 功能 | 说明 | 状态 |
|------|------|------|
| **元素级标注** | 画布元素上添加批注 (Sparkles) | 已有 |
| **页面级标注** | scope=page，不绑定元素 | ✅ 新增 |
| 双粒度切换 | 全部/元素/页面三级过滤 | ✅ 新增 |
| 标注颜色分类 | 按颜色区分标注类型 | 已有 |
| AI 执行标注 | Prompt → AI 修改标注 | ✅ 增强 |
| **直接 LLM** | 绕过 ACP，直接调 API | ✅ 新增 |
| **版本管理** | 自动 diff + 版本历史 | ✅ 新增 |
| 版本时间轴 | 列表/Diff/创建/回滚 | ✅ 新增 |
| 清空批注 | 一键清空所有批注 | 已有 |

### 2.4 知识库

| 功能 | 说明 | 状态 |
|------|------|------|
| 5 种条目类型 | term/decision/constraint/feedback/rule | ✅ 已实现 |
| **项目知识库** | scope=project，关联项目 | ✅ 新增 |
| **团队知识库** | scope=team，跨项目共享 | ✅ 新增 |
| 全文搜索 | 标题/内容模糊搜索 | ✅ 已实现 |
| AI 自动抽取 | 关键词预检 + LLM 提取 | ✅ 已实现 |
| 标签管理 | 自定义标签筛选 | ✅ 已实现 |

### 2.5 AI 能力

| 功能 | 说明 | 状态 |
|------|------|------|
| **直接 LLM 调用** | OpenAI 兼容 API，浏览器直接 fetch | ✅ 新增 |
| **模型路由** | 三级路由 (simple/medium/complex) | ✅ 新增 |
| **LangGraph Agents** | 4 个 Agent 工作流 | ✅ 新增 |
| ACP 集成 | 独立 AI 运行时 (iframe) | 已有 |
| 全局状态条 | AI 运行状态实时显示 | ✅ 新增 |
| Context Bundle | 结构化上下文交付 | ✅ 新增 |
| Prompt Pack | 角色化 Prompt 模板 | ✅ 新增 |

### 2.6 发布与导出

| 功能 | 说明 | 状态 |
|------|------|------|
| HTML ZIP 导出 | 离线 HTML 包 | 已有 |
| Axure 导出 | Axure 可消费格式 | 已有 |
| Figma 导出 | .fig 格式 | 已有 |
| **多环境发布** | 开发版/评审版/正式版通道 | ✅ 新增 |
| 发布记录 | 部署历史追踪 | ✅ 新增 |
| 仪表盘 | 通道状态总览 | ✅ 新增 |

### 2.7 工具集成

| 工具 | 用途 | 集成方式 | 状态 |
|------|------|---------|------|
| **OpenPencil MCP** | .fig 文件读写/分析/导出 | 106 个 MCP 工具 | ✅ 已配置 |
| OpenPencil 客户端 | 桌面设计编辑器 | 手动下载 | ⚠️ 需手动 |
| Pencil (pen.dev) | 轻量 Prompt-to-Design | CLI 备选 | ✅ 已安装 |
| AI PM Skill | 12 阶段 AI 产品方法论 | 全局 skill | ✅ 已安装 |

---

## 三、架构总览

### 3.1 双栈架构

```
┌──────────────────────────────────────────────────────────┐
│                    V1 （当前，React + Node.js）             │
│                                                          │
│  Frontend: React 18 + Excalidraw + Ant Design             │
│  Backend:  Node.js + TypeScript + Vite on-demand build    │
│  AI Runtime: ACP (localhost:32124) + 直接 LLM (浏览器)    │
└──────────────────────────┬───────────────────────────────┘
                           │  渐进替换中
┌──────────────────────────▼───────────────────────────────┐
│                    V2 （目标，Vue + FastAPI）              │
│                                                          │
│  Frontend: Vue 3 + Element Plus + Tauri (桌面端)          │
│  Backend:  FastAPI + Tortoise ORM + PostgreSQL/SQLite     │
│  AI Engine: OpenAI SDK + LangGraph + 4 个 Agents          │
│  Tools: OpenPencil MCP (106 tools) + Pencil (备选)       │
└──────────────────────────────────────────────────────────┘
```

### 3.2 后端技术栈 (V2)

| 组件 | 选型 | 用途 |
|------|------|------|
| Web 框架 | FastAPI 0.115+ | 异步 API 服务 |
| ORM | Tortoise ORM 1.x + asyncpg | 数据库操作 |
| 数据库 | SQLite (dev) / PostgreSQL (prod) | 数据持久化 |
| AI SDK | openai >= 1.0 | LLM 调用 |
| Agent 框架 | LangGraph | 有状态 Agent 工作流 |
| 缓存 | Redis (hiredis) | 会话/缓存 |
| 日志 | Loguru + structlog | 结构化日志 |
| 监控 | Prometheus + Sentry | 可观测性 |
| 限流 | SlowAPI | API 保护 |
| 部署 | Docker + docker-compose | 容器化部署 |

### 3.3 前端技术栈 (V2)

| 组件 | 选型 | 用途 |
|------|------|------|
| 框架 | Vue 3.4 + Composition API | 响应式 UI |
| UI 库 | Element Plus | 桌面端组件库 |
| 构建 | Vite 5 | HMR + 构建 |
| 状态管理 | Pinia | 全局状态 |
| 路由 | Vue Router 4 | SPA 路由 |
| 桌面壳 | Tauri 2.0 (Rust) | 跨平台桌面端 |

### 3.4 数据模型关系

```
Project (项目)
  ├── Prototype (原型) — 多个
  │     └── Annotation (标注) — 多个
  │           └── AnnotationVersion (版本) — 多个
  │
  ├── KnowledgeEntry (知识条目) — scope=project
  │
  └── [无直接关联, 但属于同一项目上下文]
        ├── PublishChannel (发布通道) — 3 个默认
        │     └── PublishRecord (发布记录) — 多个
        └── ContextBundle (AI 上下文) — 动态生成

Team (跨项目共享)
  └── KnowledgeEntry (知识条目) — scope=team
```

---

## 四、API 设计

### 4.1 RESTful 路由 (V2 FastAPI)

```
前缀: /v1

原型
  GET    /prototypes/          列表（分页）
  POST   /prototypes/          创建
  GET    /prototypes/{id}      详情
  PUT    /prototypes/{id}      更新
  DELETE /prototypes/{id}      删除

项目
  GET    /projects/            项目列表
  POST   /projects/            创建项目
  GET    /projects/{id}        项目详情（含原型数统计）
  PUT    /projects/{id}        更新项目
  DELETE /projects/{id}        删除项目
  GET    /projects/{id}/prototypes   项目内原型列表
  POST   /projects/{id}/prototypes   项目内创建原型

标注
  GET    /annotations/         列表（支持 ?prototype_id=）
  POST   /annotations/         创建
  PUT    /annotations/{id}     更新
  DELETE /annotations/{id}     删除
  GET    /annotations/versions/{prototype_id}  版本列表
  POST   /annotations/versions/{prototype_id}  创建版本
  POST   /annotations/versions/{prototype_id}/rollback/{version}  回滚

知识库
  GET    /knowledge/           列表（支持 ?project_id=&scope=&type=）
  POST   /knowledge/           创建条目
  GET    /knowledge/{id}       详情
  PUT    /knowledge/{id}       更新
  DELETE /knowledge/{id}       删除

发布
  GET    /publish/channels     通道列表
  PUT    /publish/channels/{id} 更新通道
  POST   /publish/channels/{id}/deploy  部署
  GET    /publish/records      发布记录
  GET    /publish/dashboard    仪表盘

AI
  GET    /ai/health            AI 服务健康检查
  POST   /ai/chat              非流式对话
  POST   /ai/chat/stream       流式对话 (SSE)
  GET    /ai/context           Context Bundle
  GET    /ai/prompt-pack       角色 Prompt 包
  POST   /ai/agents/annotate   标注执行 Agent
  POST   /ai/agents/review     多维度审查 Agent
  POST   /ai/agents/extract-knowledge  知识抽取 Agent
```

### 4.2 统一响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}

// 分页
{
  "code": 200,
  "message": "success",
  "data": {
    "data": [...],
    "total": 42,
    "current_page": 1,
    "last_page": 5,
    "per_page": 10
  }
}
```

---

## 五、AI 引擎设计

### 5.1 调用链路

```
用户输入 Prompt
    │
    ├── 浏览器端直接 LLM (已配置 API Key)
    │   └── fetch → OpenAI 兼容 API → 返回结果
    │
    └── 服务端 ACP (未配置直接 LLM)
        └── FastAPI → LLMService → OpenAI SDK → LLM
                └── ModelRouter (三级路由)
                    ├── simple → gpt-4o-mini
                    ├── medium → gpt-4o
                    └── complex → o3-mini
```

### 5.2 LangGraph Agents

| Agent | 工作流 | 节点 |
|-------|--------|------|
| **原型生成** | 分析→布局→生成→审查 | analyze → plan_layout → generate → review |
| **标注执行** | 分析→草稿→验证→重试 | analyze → draft → verify (retry ≤3) |
| **知识抽取** | 关键词预检→LLM→去重 | hasTriggerKeywords → extract → parse → dedup |
| **多维度审查** | 功能→安全→UX→汇总 | review_function → review_security → review_ux → summarize |

---

## 六、数据模型 (SQL)

### 6.1 核心表

```sql
-- 项目
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT DEFAULT '',
    create_time TIMESTAMPTZ DEFAULT NOW(),
    update_time TIMESTAMPTZ DEFAULT NOW(),
    delete_time TIMESTAMPTZ
);

-- 原型
CREATE TABLE prototypes (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    name VARCHAR(255) NOT NULL,
    description TEXT DEFAULT '',
    page_id VARCHAR(255) DEFAULT '',
    canvas_data JSONB DEFAULT '{}',
    create_time TIMESTAMPTZ DEFAULT NOW(),
    update_time TIMESTAMPTZ DEFAULT NOW(),
    delete_time TIMESTAMPTZ
);

-- 标注
CREATE TABLE annotations (
    id SERIAL PRIMARY KEY,
    prototype_id INTEGER REFERENCES prototypes(id),
    title VARCHAR(255) DEFAULT '',
    annotation_text TEXT DEFAULT '',
    markdown TEXT DEFAULT '',
    color VARCHAR(32) DEFAULT '#1677FF',
    scope VARCHAR(16) DEFAULT 'element',  -- element | page
    locator JSONB DEFAULT '{}',
    page_id VARCHAR(255) DEFAULT '',
    status VARCHAR(32) DEFAULT 'active',
    create_time TIMESTAMPTZ DEFAULT NOW(),
    update_time TIMESTAMPTZ DEFAULT NOW(),
    delete_time TIMESTAMPTZ
);

-- 版本
CREATE TABLE annotation_versions (
    id SERIAL PRIMARY KEY,
    prototype_id INTEGER REFERENCES prototypes(id),
    version INTEGER NOT NULL,
    diff JSONB DEFAULT '[]',
    summary VARCHAR(512) DEFAULT '',
    tags JSONB DEFAULT '[]',
    status VARCHAR(32) DEFAULT 'draft',  -- draft | review | released
    create_time TIMESTAMPTZ DEFAULT NOW(),
    delete_time TIMESTAMPTZ
);

-- 知识条目
CREATE TABLE knowledge_entries (
    id SERIAL PRIMARY KEY,
    type VARCHAR(32) NOT NULL,  -- term|decision|constraint|user-feedback|design-rule
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    tags JSONB DEFAULT '[]',
    source VARCHAR(512) DEFAULT '',
    scope VARCHAR(16) DEFAULT 'project',  -- project | team
    project_id INTEGER REFERENCES projects(id),
    create_time TIMESTAMPTZ DEFAULT NOW(),
    update_time TIMESTAMPTZ DEFAULT NOW(),
    delete_time TIMESTAMPTZ
);

-- 发布通道
CREATE TABLE publish_channels (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    type VARCHAR(32) NOT NULL,  -- development|review|production
    base_url VARCHAR(512) DEFAULT '',
    access_control VARCHAR(32) DEFAULT 'team',
    current_version INTEGER DEFAULT 0,
    status VARCHAR(32) DEFAULT 'pending',
    create_time TIMESTAMPTZ DEFAULT NOW(),
    update_time TIMESTAMPTZ DEFAULT NOW(),
    delete_time TIMESTAMPTZ
);

-- 发布记录
CREATE TABLE publish_records (
    id SERIAL PRIMARY KEY,
    channel_id INTEGER REFERENCES publish_channels(id),
    version INTEGER NOT NULL,
    summary VARCHAR(512) DEFAULT '',
    status VARCHAR(32) DEFAULT 'published',
    error TEXT DEFAULT '',
    create_time TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 七、项目结构

```
D:\Projects\Axhub-Make\
├── backend/                    # FastAPI 后端 (V2)
│   ├── main.py                 # 应用入口 + 中间件栈
│   ├── config/                 # pydantic-settings + Tortoise ORM
│   ├── models/                 # 7 张数据表 (Project, Prototype, Annotation, Version, Knowledge, Channel, Record)
│   ├── api/
│   │   ├── controllers/        # 业务逻辑层
│   │   ├── schemas/            # Pydantic 请求/响应
│   │   └── router/v1/          # 6 个路由模块
│   ├── ai/
│   │   ├── llm.py              # OpenAI SDK 封装
│   │   ├── router.py           # 三级模型路由
│   │   ├── context_bundle.py   # Context Bundle + Prompt Pack
│   │   └── agents/             # 4 个 LangGraph Agent
│   ├── middlewares/            # 认证 + 异常捕获
│   ├── utils/tools/            # 日志/缓存/SSE/迁移
│   └── tests/                  # pytest 测试
│
├── frontend/                   # Vue 前端 (V2)
│   ├── src/
│   │   ├── layouts/            # 顶栏导航布局
│   │   ├── pages/              # 7 个功能页面
│   │   ├── api/                # API 客户端
│   │   └── stores/             # Pinia 状态管理
│   └── src-tauri/              # Tauri 桌面壳配置
│
├── PRD.md                      # 产品需求文档
├── REFACTOR-PLAN.md            # 重构总方案
└── REFACTOR-PLAN-BACKEND.md    # 后端专项方案
```

---

## 八、竞品对比

| 维度 | Axhub Make 2.0 | ProtoLink |
|------|---------------|-----------|
| **定位** | AI 产品工作流平台 | AI IDE 交付整理工具 |
| **项目** | ✅ 以项目为核心组织所有数据 | ❌ 无明确项目概念 |
| **原型生成** | ✅ AI + Excalidraw 画布 | ❌ 依赖外部 AI IDE |
| **标注** | ✅ 元素级 + 页面级双粒度 | ✅ 页面级绑定 |
| **版本管理** | ✅ 自动 diff + 版本历史 | ✅ 迭代版本 |
| **知识库** | ✅ 项目级 + 团队级 | ⏳ 路线图中 |
| **PRD 生成** | ⏳ 待实现 | ✅ 核心功能 |
| **AI IDE 集成** | ⏳ 通过 scan CLI | ✅ Cursor/Trae/Codex |
| **导出** | ✅ Axure/Figma/HTML | ❌ 未公开 |
| **AI 调用** | ✅ 直接 LLM + ACP 双模式 | 未知 |
| **桌面端** | ✅ Tauri (开发中) | ❌ Web only |
| **开源** | ✅ MIT | ❌ SaaS |

---

## 九、开发路线图

### 已完成

| # | 模块 | 交付物 |
|---|------|--------|
| 1 | **项目管理** | Project 模型 + CRUD API + 项目内原型嵌套 |
| 2 | **知识库** | project/team 双范围 + 5 种条目 + AI 抽取 |
| 3 | **版本管理** | diff 算法 + 版本 API + 前端时间轴 |
| 4 | **多环境发布** | 3 个默认通道 + 部署记录 + 仪表盘 |
| 5 | **双粒度标注** | scope 字段 + API + ViewerWrapper |
| 6 | **直接 LLM** | 全局 tryDirectLlmFirst + 设置 UI |
| 7 | **AI 引擎** | 模型路由 + 4 个 LangGraph Agent |
| 8 | **Vue 前端** | Element Plus + 7 个页面 + 顶栏导航 |
| 9 | **FastAPI 后端** | 7 张表 + 6 个 Router + Tortoise ORM |

### 进行中

| # | 模块 | 进度 |
|---|------|------|
| 1 | **Tauri 桌面壳** | 配置就绪，需在服务器上编译 |
| 2 | **数据迁移工具** | JSON → PostgreSQL |
| 3 | **Context Bundle** | 服务端就绪，前端展示待完善 |

### 规划中

| # | 模块 | 优先级 | 估算 |
|---|------|--------|------|
| 1 | AI IDE 深度集成 | 高 | 2-3 周 |
| 2 | PRD 自动生成 | 高 | 2-3 周 |
| 3 | VS Code 扩展 | 中 | 1 周 |
| 4 | 团队协作 (多人同时编辑) | 中 | 3-4 周 |
| 5 | 第三方集成 (飞书/钉钉) | 低 | 2 周 |

---

## 十、启动与部署

### 开发环境

```bash
# 后端 (Python 3.11+)
cd backend
pip install -r requirements.txt  # 或 uv sync
uvicorn main:app --reload --port 8001

# 前端 (Node.js 18+)
cd frontend
npm install
npm run dev

# 浏览器打开
# http://localhost:5173
```

### 生产部署

```bash
# 后端
cd backend
docker-compose up -d

# 桌面端
cd frontend
npm run tauri:build
# → 产出在 src-tauri/target/release/bundle/
```

### 环境变量

```env
# 后端 .env
DEBUG=true
DB_HOST=localhost
DB_PORT=5432
DB_USER=axhub
DB_PASSWORD=axhub_secret
DB_NAME=axhub_make
AI_API_KEY=sk-...
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4o
```

---

*本文档基于全会话实施成果整理，随开发持续更新。*
