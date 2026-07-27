# Axhub Make 2.0 — 完整实施计划

> 基于与 ProtoLink 的对比分析和项目深度调研，规划从当前版本到下一代 AI 产品工作流平台的演进路线。
>
> 本计划重点集成 **OpenPencil**（开源 Figma 兼容设计编辑器，MIT 许可，106 个 MCP 工具）作为核心外部设计引擎，在原有 Axhub Make 工作流中增加一个**可选环节：UI 图生成**——将 Excalidraw 原型或已有设计稿通过 OpenPencil 转化为可编辑的 `.fig` 精稿。
>
> 同时保留 **Pencil/pen.dev**（闭源 AI 设计生成 CLI）作为轻量级设计探索的备选工具。

---

## 总体路线图

```
阶段一 (2-3周) ─── 迭代版本管理       ← 优先级最高，补齐最大差距
     ↓
阶段二 (1-2周) ─── AI IDE 扫描导入    ← 降低使用门槛
     ↓
阶段三 (2-3周) ─── 下游 AI 交付        ← 生态兼容性
     ↓
阶段四 (3-4周) ─── 产品知识库          ← 长期差异化
     ↓
阶段五 (1-2周) ─── 多环境发布+预览增强  ← 企业交付流程
     ↓
阶段六 (2周)   ─── 双粒度标注融合      ← 范式创新

┌──────────────────────────────────────────────────┐
│ 贯穿引擎: OpenPencil (MCP, 106个工具)              │
│                                                    │
│  新增可选环节: Excalidraw 原型 → OpenPencil UI 图  │
│               → .fig 精稿 → 标注/导出/交付          │
└──────────────────────────────────────────────────┘
```

**总工期：11-16 周（1 人全职）**

---

## 阶段一：迭代版本管理（高优先级，2-3 周）

### 目标
在 `annotation-source.json` 中引入版本历史机制，支持标注变更的 diff 记录、版本快照、回滚和交付说明。让 Axhub Make 拥有与 ProtoLink 同级的迭代管理能力。

### 技术方案

#### 1.1 数据模型扩展（第 1-2 天）

在 `annotation-source.json` 的 `data` 块增加版本历史字段：

```typescript
// 新增类型定义 (src/server/managementApi.prototypeAnnotation.ts)
type AnnotationVersion = {
  version: number;           // 递增版本号
  parentVersion?: number;    // 父版本号（支持分支/回滚）
  timestamp: number;         // 创建时间
  author?: string;           // 操作人
  summary: string;           // 交付说明/变更摘要
  diff: AnnotationDiff[];    // 变更差异列表
  tags?: string[];           // 版本标签（如 "交付v1", "评审版"）
  status?: 'draft' | 'review' | 'released';  // 版本状态
};

type AnnotationDiff = {
  nodeId: string;
  type: 'created' | 'updated' | 'deleted';
  field?: string;            // 变更字段（title / annotationText / color / markdown）
  before?: unknown;
  after?: unknown;
};
```

**修改文件**：
- `src/server/managementApi.prototypeAnnotation.ts` — 添加 `AnnotationVersion`、`AnnotationDiff` 类型，扩展 `AnnotationSourceDocument.data`
- `client/src/prototypes/annotation-demo/annotation-source.json` — 同步更新演示数据

#### 1.2 版本追踪钩子（第 3-5 天）

在 `writeAnnotationSource()` 和 `writeNodeMarkdown()` 中嵌入版本追踪逻辑：

```typescript
// writeAnnotationSource() 改造思路
function writeAnnotationSource(resolved: ResolveResult, source: AnnotationSourceDocument): void {
  const prevSource = readAnnotationSourceIfExists(resolved);
  const diff = computeAnnotationDiff(prevSource?.data.nodes, source.data.nodes);
  
  if (diff.length > 0) {
    const lastVersion = source.data.versions?.[source.data.versions.length - 1]?.version ?? 0;
    const versionEntry: AnnotationVersion = {
      version: lastVersion + 1,
      parentVersion: lastVersion,
      timestamp: Date.now(),
      summary: generateAutoSummary(diff),  // AI 自动生成或手动填写
      diff,
      status: 'draft',
    };
    source.data.versions = [...(source.data.versions ?? []), versionEntry];
  }
  
  // 写入文件（不变）
  fs.writeFileSync(resolved.sourceFilePath, JSON.stringify(source, null, 2), 'utf8');
}
```

**新增函数**：
- `computeAnnotationDiff(oldNodes, newNodes) → AnnotationDiff[]` — 对比前后节点数组，生成差异列表
- `generateAutoSummary(diff) → string` — 根据差异自动生成中文摘要，如 "新增 2 个标注，修改 1 个标注颜色"
- `readAnnotationSourceIfExists(path) → AnnotationSourceDocument | null` — 读取前一个版本用于 diff

**修改文件**：
- `src/server/managementApi.prototypeAnnotation.ts` — 在 `writeAnnotationSource` 和 `writeNodeMarkdown` 中注入版本追踪

#### 1.3 版本管理 API（第 6-8 天）

新增 4 个 HTTP 路由：

| 路由 | 方法 | 功能 |
|------|------|------|
| `GET /api/prototype-annotation/versions` | GET | 获取指定原型的版本列表 |
| `GET /api/prototype-annotation/versions/:id` | GET | 获取某版本的完整快照 |
| `POST /api/prototype-annotation/versions` | POST | 创建手动版本（标记发布节点） |
| `POST /api/prototype-annotation/versions/:id/rollback` | POST | 回滚到指定版本 |

```typescript
// 路由示例实现
function handleVersionApi(req, res, context, url): boolean {
  if (url.pathname === '/api/prototype-annotation/versions') {
    if (req.method === 'GET') {
      // 返回版本列表（不含 diff 详细，只含 summary/timestamp/version/status）
    }
    if (req.method === 'POST') {
      // 手动创建一个版本标记（例如 "交付v1"），带上用户填写的 summary 和 tags
    }
  }
  if (req.method === 'POST' && url.pathname.match(/^\/api\/prototype-annotation\/versions\/\d+\/rollback$/)) {
    // 回滚：读取指定版本的快照节点数据，替换当前 data.nodes，写入新版本
  }
}
```

**修改文件**：
- `src/server/managementApi.prototypeAnnotation.ts` — 新增版本路由

#### 1.4 前端版本管理 UI（第 9-14 天）

在管理界面中增加版本管理面板：

**组件清单**：
- `src/index/components/VersionCards.tsx`（已存在）— 增强为版本时间轴视图
- `src/index/components/VersionManager.tsx`（已存在）— 增强为版本详情面板
- `src/index/components/VersionCollaborationPanel.tsx`（已存在）— 增强为版本发布面板

**新增 UI 功能**：
1. **版本时间轴** — 左侧纵向时间轴，显示每个版本的序号、摘要、时间、创建者
2. **版本 Diff 视图** — 选中版本后，高亮显示哪些标注节点新增/修改/删除，支持折叠展开
3. **创建版本对话框** — 手动创建版本时填写交付说明、选择标签（draft/review/released）
4. **回滚确认对话框** — 确认回滚到指定版本，提示当前未保存的变更会丢失
5. **版本标签徽章** — 在标注列表中显示当前标注属于哪个版本

**修改文件**：
- `src/index/components/VersionCards.tsx`
- `src/index/components/VersionManager.tsx`
- `src/index/components/VersionCollaborationPanel.tsx`
- `src/index/components/content/canvas-embeds/AnnotationOverlay.tsx` — 在标注徽章旁增加版本标识

### 交付物
- [ ] 扩展的 `annotation-source.json` schema，向后兼容
- [ ] 版本追踪钩子，每次标注变更自动记录 diff
- [ ] 4 个版本管理 API 端点
- [ ] 前端版本时间轴、Diff 视图、创建和回滚 UI

---

## 阶段二：AI IDE 项目扫描与导入（高优先级，1-2 周）

### 目标
提供 CLI 工具或 VS Code 扩展，自动扫描指定目录下的前端项目（React/Vue 等），识别可交付的页面资产，自动生成 Axhub Make 原型目录和 `client.json`。

### 技术方案

#### 2.1 CLI 工具设计（第 1-3 天）

```bash
npx @axhub/make scan [project-dir] [options]
# 选项：
#   --framework auto|react|vue  指定框架（默认自动检测）
#   --entry ./src               入口目录（默认自动查找 package.json）
#   --out-dir ./                输出目录（默认当前目录）
#   --init                     同时初始化 client.json
```

**扫描规则**：

| 框架 | 识别方式 | 页面特征 |
|------|---------|---------|
| React | `package.json` 含 `react`，查找 `src/**/index.tsx` | 默认导出组件的文件 |
| Vue | `package.json` 含 `vue`，查找 `src/**/*.vue` | 含 `<template>` 的 SFC |
| 通用 | 查找 `src/**/index.html` | 含 `<body>` 的 HTML |

**输出**：
```
.axhub/make/
├── client.json         # 项目身份
└── sidebar-tree.json   # 自动识别的页面树
```

**新增文件**：
- `src/cli/scan.ts` — CLI 入口
- `src/cli/detectors/react-detector.ts` — React 项目检测
- `src/cli/detectors/vue-detector.ts` — Vue 项目检测
- `src/cli/generators/client-json-generator.ts` — 生成 client.json
- `src/cli/generators/sidebar-generator.ts` — 生成侧边栏树

#### 2.2 VS Code 扩展（第 4-7 天）

提供 VS Code 扩展，在项目侧边栏中显示"导入到 Axhub Make"按钮：

**扩展能力**：
1. 右键项目目录 → "导入到 Axhub Make"
2. 自动检测框架类型
3. 选择要导入的页面文件
4. 一键生成 `client.json` 和 `sidebar-tree.json`
5. 可选：自动启动 `make dev`

**新增仓库**（或 monorepo 内新包）：
- `extensions/vscode/package.json`
- `extensions/vscode/src/extension.ts`
- `extensions/vscode/src/commands/import-project.ts`

#### 2.3 与现有 API 集成（第 8-10 天）

将扫描结果通过现有 API 写入：

```typescript
// 复用 prototype-annotation 的 enable API
// 扫描后自动调用 POST /api/prototype-annotation/enable
// 为每个识别的页面创建 annotation-source.json 并注入 AnnotationViewer
```

**修改文件**：
- `src/server/managementApi.prototypeAnnotation.ts` — 增加批量启用接口
- `client/.axhub/make/client.json` — 更新项目信息

### 交付物
- [ ] `@axhub/make scan` CLI 命令，支持 React/Vue/通用项目
- [ ] VS Code 扩展（导入按钮）
- [ ] 批量原型启用 API

---

## 阶段三：下游 AI 结构化交付（高优先级，2-3 周）

### 目标
在导出 HTML 和 Axure 时，附带面向 AI 的结构化交付物（Context Bundle、Requirement Package），让 Cursor、Claude Code、TRAE 等 AI IDE 能直接消费。

### 技术方案

#### 3.1 AI Context Bundle 格式定义（第 1-2 天）

```typescript
type AiContextBundle = {
  schemaVersion: 1;
  project: {
    id: string;
    name: string;
    description?: string;
  };
  pages: AiPageContext[];
  annotations: AiAnnotationContext[];
  designTokens?: AiDesignTokens;
  versionInfo?: {
    version: number;
    summary: string;
  };
};

type AiPageContext = {
  id: string;
  title: string;
  route: string;
  description?: string;
  states: string[];           // 页面状态列表（空态/异常态/成功态等）
  relatedAnnotations: string[];  // 关联标注 ID
};

type AiAnnotationContext = {
  id: string;
  title: string;
  summary: string;            // annotationText 或 markdown 的前 200 字摘要
  color: string;
  priority?: 'high' | 'medium' | 'low';
  pageId: string;
  locator?: string;           // CSS 选择器
};
```

**新增文件**：
- `src/server/ai-context/types.ts` — 类型定义
- `src/server/ai-context/bundle-builder.ts` — 从 `annotation-source.json` 构建 Context Bundle

#### 3.2 Prompt Pack 生成器（第 3-5 天）

生成可直接粘贴到 AI IDE 对话中的 Prompt 片段：

```typescript
// ai-context/prompt-pack.ts
type PromptPack = {
  contextPrompt: string;     // 项目上下文描述
  pagePrompts: Record<string, string>;  // 每个页面的上下文 Prompt
  taskPrompts: {             // 面向不同角色的任务 Prompt
    engineering: string;     // "请实现以下页面..."
    testing: string;         // "请对以下功能进行测试..."
    review: string;          // "请评审以下需求的实现..."
  };
};
```

**新增文件**：
- `src/server/ai-context/prompt-pack.ts` — Prompt Pack 生成
- `src/server/ai-context/templates/engineering.md` — 工程 Prompt 模板
- `src/server/ai-context/templates/testing.md` — 测试 Prompt 模板
- `src/server/ai-context/templates/review.md` — 评审 Prompt 模板

#### 3.3 导出集成（第 6-10 天）

在现有导出 API 中附加 AI Context Bundle：

```typescript
// 修改 streamExportHtmlArchive() (managementApi.exports.ts)
// 在 ZIP 包中增加 ai/ 目录：
//   export-<name>/
//   ├── index.html
//   ├── assets/
//   ├── ai/
//   │   ├── context-bundle.json       # AI Context Bundle
//   │   ├── prompt-pack.md            # Prompt Pack
//   │   ├── annotation-source.json    # 完整标注源（供 AI 参考）
//   │   └── manifest.json             # 清单文件
//   └── ...
```

在管理界面增加"复制 AI Prompt"按钮：

```typescript
// 新增 API 路由
// GET /api/export-ai-context?targetPath=prototypes/<id>&version=<version>
// 返回 JSON: { contextBundle, promptPack }
```

**修改文件**：
- `src/server/managementApi.exports.ts` — AI 上下文打包 + 新路由
- `src/server/axureExportCodeWrap.ts` — Axure 导出时附送 AI Context
- `src/index/domains/export/` — 界面增加"复制 AI Prompt"按钮

#### 3.4 管理界面 AI 交付面板（第 11-14 天）

在管理界面增加"AI 交付"面板：
1. 展示当前原型的 AI Context 摘要
2. "一键复制 Context Prompt" 按钮
3. "下载 AI 交付包" 按钮
4. 角色选择（研发/测试/评审）→ 生成对应角色 Prompt

**修改文件**：
- `src/index/domains/export/AiDeliveryPanel.tsx` — 新增 AI 交付面板
- `src/index/components/SettingsDialog.tsx` — 集成 AI 交付入口

### 交付物
- [ ] AI Context Bundle 格式定义和构建器
- [ ] Prompt Pack 生成器（研发/测试/评审角色模板）
- [ ] 导出时自动附带 `ai/` 目录
- [ ] 管理界面 AI 交付面板

---

## 阶段四：产品知识库（中优先级，3-4 周）

### 目标
构建项目历史沉淀机制，将设计决策、术语表、约束条件等产品知识持久化，让新原型生成时自动继承项目上下文。

### 技术方案

#### 4.1 知识库数据模型（第 1-2 天）

```typescript
type KnowledgeBase = {
  schemaVersion: 1;
  projectId: string;
  entries: KnowledgeEntry[];
  updatedAt: number;
};

type KnowledgeEntry = {
  id: string;
  type: 'term' | 'decision' | 'constraint' | 'user-feedback' | 'design-rule';
  title: string;
  content: string;           // Markdown 正文
  tags: string[];
  source?: string;           // 来源（对话 ID / 原型 ID / 手动录入）
  createdAt: number;
  updatedAt: number;
  relatedEntryIds?: string[];
};
```

**新增文件**：
- `src/server/knowledge-base/types.ts`
- `src/server/knowledge-base/knowledge-store.ts` — 读写知识库 JSON
- `src/server/knowledge-base/knowledge-api.ts` — CRUD API

#### 4.2 知识库 CRUD API（第 3-5 天）

| 路由 | 方法 | 功能 |
|------|------|------|
| `GET /api/knowledge-base` | GET | 查询知识库（支持 tags 过滤） |
| `POST /api/knowledge-base/entries` | POST | 新增知识条目 |
| `PUT /api/knowledge-base/entries/:id` | PUT | 更新知识条目 |
| `DELETE /api/knowledge-base/entries/:id` | DELETE | 删除知识条目 |
| `GET /api/knowledge-base/search?q=` | GET | 全文搜索知识库 |

#### 4.3 AI 知识抽取管道（第 6-10 天）

在标注/评审过程中自动抽取知识：

```typescript
// 新增服务: knowledge-base/extractor.ts
// 钩子场景：
// 1. 标注创建/更新时 → 提取术语和设计决策
// 2. 评审完成时 → 提取用户反馈
// 3. 对话结束后 → 提取共识和约束
// 4. 原型生成后 → 提取设计规则

// 使用 LLM 调用，示例 Prompt：
// "从以下产品对话中提取产品术语、设计决策和约束条件，
//  每项以结构化 JSON 输出。"
```

#### 4.4 管理界面知识库面板（第 11-14 天）

- 知识库浏览页面（类型筛选、全文搜索）
- 新增/编辑知识条目对话框
- 知识来源追溯（标注 → 知识条目的双向链接）
- AI 自动抽取结果的审核面板

#### 4.5 原型生成集成（第 15-21 天）

在 AI 生成原型时自动注入知识库上下文：

```typescript
// 修改 onDemandBuild.ts 或生成流程
// 在 AI 生成 Prompt 中自动附加知识库内容：
// "项目术语：{...} 设计决策：{...} 约束条件：{...}"
```

**新增文件**：
- `src/server/knowledge-base/` 整个目录
- `src/index/components/knowledge/` 整个目录

### 交付物
- [ ] 知识库数据模型和持久化存储
- [ ] 5 个 CRUD API 端点
- [ ] AI 自动知识抽取管道
- [ ] 管理界面知识库面板
- [ ] 原型生成时的知识注入

---

## 阶段五：多环境发布与 Preview Shell 增强（中优先级，1-2 周）

### 目标
引入发布通道概念（开发版/评审版/正式版），增强预览仪表盘，支持多环境部署。

### 技术方案

#### 5.1 发布通道模型（第 1-2 天）

```typescript
type PublishChannel = {
  id: string;
  name: string;               // "开发版" / "评审版" / "正式版"
  type: 'development' | 'review' | 'production';
  baseUrl?: string;           // 部署基础 URL
  accessControl?: 'public' | 'team' | 'invite-only';
  version?: number;           // 当前发布版本
  publishedAt?: number;
  status: 'pending' | 'published' | 'failed';
};
```

**新增文件**：
- `src/server/publish/types.ts`
- `src/server/publish/publish-api.ts`

#### 5.2 发布 API（第 3-5 天）

| 路由 | 方法 | 功能 |
|------|------|------|
| `GET /api/publish/channels` | GET | 获取所有发布通道 |
| `POST /api/publish/channels` | POST | 创建发布通道 |
| `POST /api/publish/channels/:id/deploy` | POST | 部署到指定通道 |
| `GET /api/publish/channels/:id/versions` | GET | 通道的发布历史 |

#### 5.3 项目仪表盘（第 6-10 天）

在管理界面首页增加仪表盘视图：

```
项目名称: xxx
├── 原型总数: 12
├── 已标注: 8 (67%)
├── 当前版本: v3
├── 最后更新: 2026-07-27
├── 发布通道:
│   ├── 开发版  → 在线预览 (更新时间)
│   ├── 评审版  → 在线预览 (更新时间)
│   └── 正式版  → 在线预览 (更新时间)
└── 最近活动:
    ├── [2h前] 张三 更新了 "首页" 标注
    ├── [5h前] 李四 发布了 v2 评审版
    └── [1d前] 系统 自动创建了版本 v3
```

**新增文件**：
- `src/index/components/dashboard/ProjectDashboard.tsx`
- `src/index/components/dashboard/ActivityFeed.tsx`
- `src/index/components/dashboard/PublishStatusCard.tsx`

### 交付物
- [ ] 发布通道模型和 API
- [ ] 项目仪表盘 UI
- [ ] 一键部署到多环境功能

---

## 阶段六：页面+元素双粒度标注融合（中优先级，2 周）

### 目标
在 `annotation-source.json` 中同时支持页面级标注（整页绑需求）和元素级标注（精确到 DOM 元素），`AnnotationViewer` 按场景切换展示模式。

### 技术方案

#### 6.1 数据模型扩展（第 1-2 天）

在现有 `data.nodes[]` 基础上增加 `scope` 字段：

```typescript
type AnnotationNode = {
  // ... 现有字段
  scope: 'element' | 'page';     // 标注粒度
  pageScope?: {
    // scope === 'page' 时有效
    route: string;               // 页面路由
    viewport?: string;           // 视口描述（"首屏" / "底部"）
    pageSelector?: string;       // 整页面选择器
  };
};
```

页面级标注的 `locator` 可选（整页不需要精确到元素），标注面板中展示为"页面级标注"标签。

#### 6.2 管理界面编辑工具增强（第 3-7 天）

在标注弹框中增加粒度切换：

```typescript
// AnnotationOverlay.tsx 增强
// 当 scope === 'page' 时：
//   - 不显示元素徽章位置
//   - 在标注列表中显示为独立条目
//   - 编辑时显示页面路由选择器

// 新增下拉选择器:
// [元素级标注] [页面级标注]
```

#### 6.3 AnnotationViewer 展示增强（第 8-10 天）

修改 `@axhub/annotation` 的展示逻辑：
- 元素级标注：保持现有 marker + 气泡模式
- 页面级标注：在侧边栏增加"页面标注"标签页，切换到对应页面时自动高亮

#### 6.4 服务端 API 兼容（第 11-14 天）

确保现有 API 对 page-scope 标注的读写支持：
- `PUT /api/prototype-annotation/node` — 接受 `scope` 字段
- `GET /api/prototype-annotation` — 返回标注时标注粒度信息

### 交付物
- [ ] 扩展的 AnnotationNode schema（scope 字段）
- [ ] 管理界面标注粒度切换 UI
- [ ] AnnotationViewer 页面级标注展示模式
- [ ] 服务端 API 兼容

---

## OpenPencil 集成：UI 图生成引擎（贯穿所有阶段）

OpenPencil 是本计划的核心外部设计引擎。它在原有 Axhub Make 工作流中新增一个**可选环节：UI 图生成**，用户可以随时将 Excalidraw 原型转为精良的 `.fig` 设计稿，获得完整的视觉稿交付能力。

### 工作流变化

```
原有流程:
  Excalidraw 原型 → 标注 → 评审 → 发布 (HTML/Axure/Figma)

新增可选环节:
  Excalidraw 原型 ─┬─→ 标注 → 评审 → 发布
                   │
                   └─→ [可选] OpenPencil UI 图生成 → .fig 精稿 → 标注/导出
                        ↓ 用 JSX Render 重新构建
                        ↓ 用 MCP 工具微调样式
                        ↓ 导出 PNG/SVG/Tailwind
```

**UI 图生成的使用场景：**
- 项目需要设计评审时，将线框图升级为像素级精稿
- 需要导出 `.fig` 文件给设计师继续编辑
- 需要生成 Tailwind CSS 代码作为开发参照
- 需要批量产出一致风格的页面截图用于方案汇报

### OpenPencil（开源，MIT）

| 属性 | 值 |
|------|-----|
| **首页** | https://openpencil.dev |
| **仓库** | github.com/open-pencil/open-pencil |
| **MCP 工具数** | 106 个 |
| **本地安装** | `npm install -g @open-pencil/mcp`，命令 `openpencil-mcp` |
| **工作模式** | 需先运行桌面应用，MCP server 通过 WebSocket 连接 |

**集成到各阶段：**

| 阶段 | 集成点 | 具体用途 |
|------|--------|---------|
| **原型生成后** | UI 图生成（新增可选环节） | 将 Excalidraw 原型用 JSX Render 重建成 OpenPencil 精稿，通过 MCP 工具微调样式、排版和配色 |
| **阶段一** 版本管理 | 设计版本可视化 | 使用 OpenPencil `export_image` 为每个版本生成视觉快照，版本时间轴中展示缩略图 |
| **阶段二** AI IDE 扫描 | Figma 项目扫描 | 扩展扫描器支持 OpenPencil 原生 `.fig` 文件，识别 Figma 设计稿中的页面资产 |
| **阶段三** AI 交付 | 设计稿上下文 | 借助 OpenPencil 的 `analyze_colors`、`analyze_typography` 等分析工具，为 AI Context Bundle 补充设计 Token 和视觉规范 |
| **阶段四** 知识库 | 设计规则抽取 | 用 OpenPencil `analyze_clusters` 检测重复设计模式（潜在组件），自动录入知识库 |
| **阶段五** 多环境发布 | 设计预览 | 用 OpenPencil `export_image` / `export_svg` 生成发布物的视觉预览图 |
| **阶段六** 双粒度标注 | 设计稿直接标注 | 页面级标注可以直接在 OpenPencil 打开的设计稿上绑定，利用其 `find_nodes` / `query_nodes` 定位目标元素 |
| **Figma 导出增强** | 导出验证 | Axhub Make 现有 `/api/export-make` 导出 `.fig` 文件后，调用 OpenPencil CLI 的 `open_file` + `get_page_tree` 验证导出完整性 |

### 可选环节：UI 图生成工作流

这是本计划在原有流程上新增的核心能力，有两种进入方式：

#### 方式 A：从 Excalidraw 原型生成（推荐）

```bash
# 1. 在 Axhub Make 中完成 Excalidraw 原型设计
# 2. 获取原型的 JSON 描述（页面结构、组件布局、文案）
# 3. 用 OpenPencil JSX Render 重建为精稿

# 示例：用 JSX 描述一个卡片组件并渲染到 OpenPencil
render(jsx=`
<Frame name="Card" w={320} h="hug" flex="column" gap={16} p={24} bg="#FFF" rounded={16}>
  <Text size={18} weight="bold" color="#1A1A1A">标题文案</Text>
  <Text size={14} color="#666" lines={2}>描述内容从这里开始...</Text>
  <Frame name="Actions" flex="row" gap={8}>
    <RECTANGLE name="Button" w={80} h={36} fill="#1677FF" cornerRadius={8} />
  </Frame>
</Frame>
`)

# 4. 用 MCP 工具微调
#    set_fill(id, gradient="left-right", color="#1677FF", color_end="#4096FF")
#    set_effects(id, type="DROP_SHADOW", color="rgba(0,0,0,0.1)", offset_y=4, radius=12)
#    set_layout(id, direction="HORIZONTAL", spacing=24, padding=32)

# 5. 导出精稿
#    export_image(ids=[...], format="PNG", scale=2)
#    save_file(path="./output/ui-design.fig")
```

#### 方式 B：从已有设计文件开始

```bash
# 1. 打开已有的 .fig 设计文件
open_file(path="./existing-design.fig")

# 2. 读取页面结构和样式
page_tree = get_page_tree()
nodes = find_nodes(name="Button")
colors = analyze_colors()
tokens = analyze_typography()

# 3. 修改或扩展设计
clone_node(id="btn-primary")
set_fill(id="btn-primary-copy", color="#52C41A")

# 4. 导出为多种格式
export_image(ids=[...], format="PNG", scale=2)
export_svg(ids=[...])
save_file(path="./output/revised-design.fig")
```

### UI 图生成的交付物

| 输出格式 | 用途 | 工具 |
|---------|------|------|
| `.fig` 文件 | 交付给设计师继续编辑 | OpenPencil `save_file` |
| PNG/WEBP（2×） | 方案汇报、评审附件 | OpenPencil `export_image` |
| SVG | 开发用矢量资源 | OpenPencil `export_svg` |
| JSX + Tailwind | 开发直接使用的组件代码 | OpenPencil JSX Render |
| Design Token JSON | 设计规范同步 | OpenPencil `design_to_tokens` |

---

## 各阶段依赖关系

```
           ┌─────────────────────────────────────┐
           │ OpenPencil (MCP, 106 tools)          │ ← 核心引擎，贯穿所有阶段
           │   ├─ Excalidraw → UI 图生成（可选）  │
           │   ├─ .fig 读写/分析/导出             │
           │   └─ JSX Render / Design Token       │
           └─────────────────────────────────────┘

阶段一 ─── 独立，无外部依赖
              │
阶段二 ─── 独立，可与阶段一并行
              │
阶段三 ─── 依赖阶段一（需要版本号用于 AI Context）
              │
阶段四 ─── 独立，可与阶段一/二并行
              │
阶段五 ─── 依赖阶段一（需要版本状态）
              │
阶段六 ─── 依赖阶段一和 @axhub/annotation 包（需发布新版）
```

**关于工具依赖：** OpenPencil 和 Pencil 不产生阶段之间的串行依赖——它们按需调用，任何时候桌面应用打开即可使用。OpenPencil MCP 需要本地运行桌面应用，因此 CI/CD 场景建议配置专用的 OpenPencil 实例或使用 HTTP 模式。

**推荐并行策略**：
- 第 1-3 周：阶段一 + 阶段二同时启动（不同开发者）
- 第 4-6 周：阶段三 + 阶段四同时启动
- 第 7-8 周：阶段五 + 阶段六同时启动

---

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| `annotation-source.json` 文件变大（版本历史累积） | 读写性能下降 | 1) 版本历史默认只保留最近 50 条 2) 提供归档 API 3) 大文件启用流式读写 |
| 版本 diff 计算在大型原型上耗时 | API 响应慢 | diff 计算异步执行，先返回主操作再后台计算 |
| AI IDE 项目扫描误判框架类型 | 生成错误的页面入口 | 扫描结果提供预览确认，用户手动校正后再写入 |
| 知识库 AI 抽取质量不稳定 | 知识条目不准确 | 抽取结果标记为"待审核"，人工确认后才进入正式知识库 |
| Vue 项目页面发现不全面 | 遗漏部分页面 | 提供手动添加页面入口，扫描结果作为"建议"而非唯一来源 |
| OpenPencil 桌面应用未运行 | MCP 工具调用失败，UI 图生成不可用 | 1) 提供清晰的错误提示，引导用户启动桌面应用 2) 支持 HTTP 模式作为备选 3) UI 图生成为可选环节，不影响核心流程 |
| Pencil 认证过期（备选工具） | 轻量级设计探索不可用 | 提示用户重新 `pen login`，无影响——核心流程不依赖 Pencil |
| OpenPencil MCP 版本与桌面应用版本不匹配 | 部分工具调用异常 | 安装时锁定 `@open-pencil/mcp` 与桌面应用同版本，启动时做版本检测 |

---

## 总计工作量

| 阶段 | 工期 | 新增文件 | 修改文件 | 核心复杂度 |
|------|------|---------|---------|-----------|
| 一：迭代版本管理 | 2-3 周 | ~5 个 | ~6 个 | ⭐⭐⭐ diff 算法 + 版本回滚安全性 |
| 二：AI IDE 扫描导入 | 1-2 周 | ~8 个 | ~2 个 | ⭐⭐ 框架检测 + CLI 设计 |
| 三：下游 AI 交付 | 2-3 周 | ~8 个 | ~4 个 | ⭐⭐ Prompt 工程 + 导出集成 |
| 四：产品知识库 | 3-4 周 | ~15 个 | ~3 个 | ⭐⭐⭐ AI 抽取 + 搜索 + UI |
| 五：多环境发布 | 1-2 周 | ~6 个 | ~3 个 | ⭐ 发布通道管理 |
| 六：双粒度标注 | 2 周 | ~3 个 | ~5 个 | ⭐⭐ AnnotationViewer 改造 |
| **OpenPencil 引擎集成** | **贯穿** | **0**（已安装） | **0** | ⭐ 按需调用，无开发工作量。新增可选 UI 图生成环节 |
| **总计** | **11-16 周** | **~45 个** | **~23 个** | |

---

## 如何开始执行

### 立即启动（第 1 天）

1. **工具就绪检查**：确认 OpenPencil MCP 已注册（`claude mcp list` 应看到 `open-pencil` 含 106 个工具）。Pencil 为备选，非必需。
2. **分支策略**：从 `main` 创建 `feat/version-management` 分支
3. **优先完成**：阶段一的 1.1 数据模型扩展（最快产出，2 天）
4. **测试先行**：为 `computeAnnotationDiff()` 和版本 API 编写单元测试，参考现有 `src/server/__tests__/prototype-annotation-api.test.ts`
5. **验证方式**：在 annotation-demo 原型上手动创建标注，确认版本历史正确记录

### 关键里程碑

| 时间 | 里程碑 | 验证方式 |
|------|--------|---------|
| 第 3 天 | 版本数据模型 + diff 算法完成 | 单元测试通过 |
| 第 8 天 | 版本管理 API 全部可用 | curl 测试 + 集成测试 |
| 第 14 天 | 前端版本管理 UI 可用 | 手动创建/回滚版本 |
| 第 21 天 | 阶段一全面交付 | 验收测试 + 演示 |
