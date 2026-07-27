# Axhub Make — 产品需求文档 (PRD)

> 版本: 2.0 (迭代中)
> 基于全会话实施成果整理

---

## 一、产品定位

Axhub Make 是一个面向 AI 产品工作流的**原型生成→标注→评审→发布**一体化平台。产品经理可以用它从需求到可交付原型全链路完成工作。

---

## 二、功能清单

### P0 — 核心功能（已有或已实现）

#### 1. 原型画布 (Excalidraw)

| 功能 | 说明 | 状态 |
|------|------|------|
| 自由绘制画布 | 支持形状、文字、箭头、分组 | 已存在 |
| AI 生成原型 | 输入 Prompt 自动生成页面原型 | 已存在 |
| 多页面管理 | 同一原型多个页面，URL Hash 路由 | 已存在 |
| 设备外壳模拟 | 手机/平板/桌面预览 | 已存在 |

#### 2. 标注系统

| 功能 | 说明 | 状态 |
|------|------|------|
| 元素级标注 | 在画布元素上添加批注 (Sparkles 徽章) | 已存在 |
| 标注弹框编辑器 | Textarea + 执行按钮 | 已存在 ✅ 增强 |
| 多颜色分类 | 标注按颜色区分类型 | 已存在 |
| AI 执行标注 | 输入需求后 AI 自动修改 | 已存在 ✅ 增强 |
| 清空所有批注 | 一键清空 | 已存在 |
| **直接 LLM 调用** | 绕过 ACP，直接调 OpenAI 兼容 API | ✅ 新增 |
| **绕过 ACP 设置** | Settings 开关 + BaseURL/APIKey/Model | ✅ 新增 |
| **页面级标注** | scope: 'page' 无元素定位的标注 | ✅ 新增 |
| **双粒度切换** | 全部/元素/页面三级过滤 (AnnotationViewerWrapper) | ✅ 新增 |
| **版本管理** | annotation-source.json 版本追踪 | ✅ 新增 |
| **版本时间轴** | 版本列表/Diff/创建/回滚 | ✅ 新增 |
| **版本 API** | GET/POST 列表 + 手动创建 + 回滚 | ✅ 新增 |
| **运行时展示** | AnnotationViewer 页面标注标签 | ✅ 新增 |

#### 3. AI 助手面板

| 功能 | 说明 | 状态 |
|------|------|------|
| ACP iframe 嵌入 | 独立 AI 运行时 (localhost:32124) | 已存在 |
| iframe 池管理 | 多实例切换 | 已存在 |
| **面板加宽** | 默认 320px → 480px | ✅ 改进 |
| **运行状态条** | 底部蓝色状态条 + 脉冲动画 | ✅ 新增 |
| **全局直接 LLM** | tryDirectLlmFirst 函数，所有 AI 入口通用 | ✅ 新增 |

#### 4. 评审与发布

| 功能 | 说明 | 状态 |
|------|------|------|
| 原型审查 | AI 驱动的原型审查 | ✅ 直接 LLM 支持 |
| HTML ZIP 导出 | 完整离线 HTML 包 | 已存在 |
| Axure 导出 | 导出为 Axure 可消费格式 | 已存在 |
| Figma 导出 | .fig 格式 | 已存在 |
| **多环境发布** | 开发版/评审版/正式版通道 | ✅ 新增 |
| **发布 API** | channels/deploy/records/dashboard | ✅ 新增 |
| **项目仪表盘** | 通道状态 / 发布记录 / 统计 | ✅ 新增 |

#### 5. 项目管理

| 功能 | 说明 | 状态 |
|------|------|------|
| 项目身份 (client.json) | 项目 ID + 名称 | 已存在 |
| 侧边栏树 (sidebar-tree.json) | 原型/文档/主题组织 | 已存在 |
| 设置对话框 | 主机/端口/模型/API Key 配置 | 已存在 |
| **AI IDE 扫描导入** | axhub-make scan CLI 命令 | ✅ 新增 |
| **框架检测** | React/Vue 自动识别 | ✅ 新增 |
| **产品知识库** | 术语/决策/约束/反馈/规则 | ✅ 新增 |
| **知识库 CRUD API** | 5 个路由端点 | ✅ 新增 |
| **AI 知识抽取** | 关键词预检 + Ollama 集成 | ✅ 新增 |
| **知识库面板** | 搜索/筛选/创建/编辑/删除 | ✅ 新增 |
| **原型生成上下文注入** | getKnowledgeContext / getPrototypeGenerationContext | ✅ 新增 |

#### 6. 工具集成

| 功能 | 说明 | 状态 |
|------|------|------|
| **OpenPencil MCP** | 106 个设计工具，自动安装 | ✅ 已配置 |
| **Pencil (pen.dev)** | AI 设计生成 CLI (备选) | ✅ 已安装 |
| **AI PM 技能** | 12 阶段 AI 产品方法论 | ✅ 已安装 |

---

## 三、用户角色

| 角色 | 核心任务 | 使用的主要功能 |
|------|---------|--------------|
| **产品经理** | 需求→原型→评审→交付 | 画布/标注/审查/发布 |
| **设计师** | 视觉精稿输出 | OpenPencil UI 图生成 /.fig 导出 |
| **开发者** | 理解需求并实现 | 标注阅读 / AI Context Bundle |
| **AI Agent** | 自动执行产品任务 | 知识库 / 上下文注入 / MCP 工具 |

---

## 四、用户流程

### 4.1 核心工作流

```
┌────────────────────────────────────────────────────────────┐
│ 1. 需求分析                                                │
│    ├── 在画布上用 AI 生成低保真原型                         │
│    └── 或在 AI IDE (Cursor/Trae) 中开发后 → axhub-make scan │
├────────────────────────────────────────────────────────────┤
│ 2. [可选] UI 图生成                                         │
│    ├── 打开 OpenPencil 桌面客户端                           │
│    ├── 用 JSX Render 从 Excalidraw 原型重建精稿             │
│    └── 导出 .fig / PNG / SVG / Design Token                 │
├────────────────────────────────────────────────────────────┤
│ 3. 标注                                                    │
│    ├── 元素级标注 (画布上选中元素 → 添加批注)                │
│    ├── 页面级标注 (scope: page，不绑定特定元素)              │
│    └── AI 自动标注 / 手动编辑                               │
├────────────────────────────────────────────────────────────┤
│ 4. 版本管理                                                │
│    ├── 每次标注修改自动记录版本                              │
│    ├── 查看版本时间轴 / Diff                                │
│    └── 回滚到指定版本                                      │
├────────────────────────────────────────────────────────────┤
│ 5. 评审                                                    │
│    ├── AI 驱动原型审查                                      │
│    └── 知识库辅助上下文                                     │
├────────────────────────────────────────────────────────────┤
│ 6. 发布                                                    │
│    ├── HTML ZIP / Axure / Figma 导出                       │
│    └── 多环境发布 (开发版/评审版/正式版)                    │
└────────────────────────────────────────────────────────────┘
```

### 4.2 AI 调用链路

```
用户输入 Prompt
    │
    ├── 检查 localStorage 直接 LLM 配置
    │   ├── 已启用 + 有 API Key
    │   │   ├── 直接 fetch OpenAI 兼容 API → 返回结果
    │   │   └── 失败 → 回退 ACP
    │   │
    │   └── 未启用
    │       ├── ACP 可用 → 通过 iframe postMessage 或服务器 API
    │       └── ACP 不可用 → 提示用户配置直接 LLM
    │
    └── 返回结果 → 显示在 UI 中
```

---

## 五、技术架构

### 5.1 前端栈

| 技术 | 用途 |
|------|------|
| React 18 + TypeScript | UI 框架 |
| Excalidraw | 画布引擎 |
| Vite | 构建工具 |
| Ant Design | UI 组件库 |
| Tailwind CSS | 样式 |
| @axhub/annotation | 标注运行时展示 |
| @axhub/commentary | 批注/评审运行时 |
| vitest | 测试 |

### 5.2 服务端栈

| 技术 | 用途 |
|------|------|
| Node.js + TypeScript | 运行时 |
| Vite on-demand build | 按需原型构建 |
| SSE (Server-Sent Events) | AI 流式响应 |
| postMessage (ACP) | 与 AI 运行时通信 |

### 5.3 外部工具

| 工具 | 用途 | 安装方式 |
|------|------|---------|
| **OpenPencil MCP** | .fig 设计文件读写/分析/导出 | `pnpm install` 自动安装 |
| **OpenPencil 客户端** | 桌面设计编辑器 | 手动下载 (https://openpencil.dev) |
| **Pencil (备选)** | 轻量 Prompt-to-Design | `npm install -g @pen.dev/cli` |

---

## 六、数据模型

### 6.1 annotation-source.json

```typescript
{
  documentVersion: 1,
  format: 'axhub-annotation-source',
  data: {
    version: 2,
    prototypeName: string,
    pageId: string,
    nodes: AnnotationNode[],       // 标注节点
    updatedAt: number,
    versions?: AnnotationVersion[], // 版本历史 (新增)
  },
  markdownMap: Record<string, string>,
  assetMap: Record<string, string>,
  directory?: AnnotationDirectory,
}
```

### 6.2 知识库 (.axhub/knowledge-base.json)

```typescript
{
  schemaVersion: 1,
  projectId: string,
  entries: KnowledgeEntry[],    // 5 种类型
  updatedAt: number,
}
```

### 6.3 发布配置 (.axhub/publish.json)

```typescript
{
  schemaVersion: 1,
  projectId: string,
  channels: PublishChannel[],   // 3 个默认通道
  records: PublishRecord[],
  updatedAt: number,
}
```

---

## 七、API 概览

| 路由 | 方法 | 功能 | 阶段 |
|------|------|------|------|
| `/api/prototype-annotation` | GET | 查询标注状态 | 已有 |
| `/api/prototype-annotation/enable` | POST | 启用标注 | 已有 |
| `/api/prototype-annotation/node` | PUT | 写入/删除标注节点 | 已有 |
| `/api/prototype-annotation/versions` | GET | 版本列表 | ✅ 新增 |
| `/api/prototype-annotation/versions` | POST | 手动创建版本 | ✅ 新增 |
| `/api/prototype-annotation/versions/:id/rollback` | POST | 回滚版本 | ✅ 新增 |
| `/api/knowledge-base` | GET | 知识库查询/搜索 | ✅ 新增 |
| `/api/knowledge-base/context` | GET | 知识库上下文 | ✅ 新增 |
| `/api/knowledge-base/entries` | POST | 创建知识条目 | ✅ 新增 |
| `/api/knowledge-base/entries/:id` | PUT | 更新知识条目 | ✅ 新增 |
| `/api/knowledge-base/entries/:id` | DELETE | 删除知识条目 | ✅ 新增 |
| `/api/publish/channels` | GET | 发布通道列表 | ✅ 新增 |
| `/api/publish/channels/:id` | PUT | 更新通道 | ✅ 新增 |
| `/api/publish/channels/:id/deploy` | POST | 部署到通道 | ✅ 新增 |
| `/api/publish/records` | GET | 发布记录 | ✅ 新增 |
| `/api/publish/dashboard` | GET | 仪表盘数据 | ✅ 新增 |
| `/api/export-index-bundle` | GET | 导出构建产物 | 已有 |
| `/api/axure-export-code` | GET | Axure 导出代码 | 已有 |
| `/api/export-html` | GET/POST | HTML ZIP 导出 | 已有 |
| `/api/export-make` | GET/POST | Figma 导出 | 已有 |

---

## 八、实施路线图

### 已完成（本次会话）

| # | 模块 | 产出 |
|---|------|------|
| 1 | **迭代版本管理** | 版本类型 + diff 算法 + 4 API + 前端面板 |
| 2 | **AI IDE 扫描导入** | axhub-make scan CLI + 框架检测 |
| 3 | **产品知识库** | 存储 + CRUD API + AI 抽取 + 上下文 |
| 4 | **多环境发布** | 通道模型 + 5 API + 仪表盘 |
| 5 | **双粒度标注** | scope 字段 + API + 前端包装组件 |
| 6 | **AI 助手体验改进** | 面板加宽 + 状态条 + 直接 LLM |
| 7 | **直接 LLM 绕过 ACP** | 全局 tryDirectLlmFirst + 设置 UI |
| 8 | **工具配置** | OpenPencil MCP + Pencil skill |

### 待完成

| # | 模块 | 优先级 | 估算 |
|---|------|--------|------|
| 1 | **下游 AI 交付 (Context Bundle)** | 高 | 2-3 周 |
| 2 | **VS Code 扩展** | 中 | 1 周 |
| 3 | **ACP iframe 直接 LLM 支持** | 中 | 需修改 ACP 应用 |
| 4 | **知识库 AI 抽取体验完善** | 中 | 1 周 |
| 5 | **发布通道部署自动化** | 低 | 1 周 |

---

## 九、竞品对比

| 维度 | Axhub Make | ProtoLink | 各自优势 |
|------|-----------|-----------|---------|
| 原型生成 | ✅ Excalidraw + AI 生成 | ❌ 无 | Axhub Make 可产出原型 |
| 页面资产发现 | ✅ axhub-make scan | ✅ 自动扫描 | ProtoLink 更深度集成 IDE |
| 需求标注 | ✅ 元素级 + 页面级 | ✅ 页面级 | Axhub Make 粒度更细 |
| 版本管理 | ✅ 标注版本追踪 | ✅ 迭代管理 | 两者方向不同 |
| PRD 生成 | 待实现 | ✅ 核心功能 | ProtoLink 更强 |
| AI IDE 集成 | 待完善 | ✅ Cursor/Trae/Codex | ProtoLink 更强 |
| 导出能力 | ✅ Axure/Figma/HTML | ❌ 未公开 | Axhub Make 更强 |
| 开源 | ✅ 是 | ❌ SaaS | Axhub Make 可自托管 |
| AI 调用 | ✅ 直接 LLM + ACP | 未知 | Axhub Make 灵活 |
| 产品知识库 | ✅ 已实现 | ✅ 路线图中 | Axhub Make 已领先 |

---

## 十、安装部署

### 开发环境

```bash
git clone <repo>
cd axhub-make
pnpm install
pnpm dev
```

### 依赖检查

| 项目 | 命令 |
|------|------|
| OpenPencil MCP | `npx openpencil-mcp --help` |
| OpenPencil 桌面客户端 | 手动下载 https://openpencil.dev |
| ACP (可选) | `npx @axhub/acp --port 32124` |
| 直接 LLM (替代 ACP) | 在设置中填入 API Key |
