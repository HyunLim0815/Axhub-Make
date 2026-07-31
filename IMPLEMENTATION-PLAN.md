# Axhub Make 2.0 — 全功能补齐实施计划

> 基于 V1 (React/Node.js) 的完整功能，在 V2 (FastAPI + Vue 3) 上重新实现。
> 目标：V2 后端和前端完整覆盖 V1 的所有功能。

---

## 总体策略

```
阶段一 (✅ 完成) ─── 后端缺失功能补齐
     │
阶段二 (✅ 完成) ─── Vue 前端重写
     │
阶段三 (✅ 完成) ─── 前后端联调 + 集成验证
```

---

## 阶段一：后端缺失功能补齐（✅ 已完成）

### 1.1 文件操作模块 ✅
| 文件 | 说明 |
|------|------|
| `backend/api/schemas/file_ops.py` | 文件上传/复制/重命名/删除的 Schema |
| `backend/api/controllers/FileOpsController.py` | 文件操作控制器 |
| `backend/api/router/v1/file_ops.py` | 路由 |
| 新增 API | `POST /v1/files/upload`, `POST /v1/files/delete`, `POST /v1/files/copy`, `POST /v1/files/rename` |

### 1.2 媒体资源管理 ✅
| 文件 | 说明 |
|------|------|
| `backend/models/media.py` | MediaFile 模型 |
| `backend/api/schemas/media.py` | Schema |
| `backend/api/controllers/MediaController.py` | 媒体资源控制器（列表/上传/删除） |
| `backend/api/router/v1/media.py` | 路由 |
| 新增 API | `GET /v1/media`, `POST /v1/media/upload`, `POST /v1/media/folder`, `DELETE /v1/media/{id}`, `GET /v1/media/file/{path}` |

### 1.3 文档管理 ✅
| 文件 | 说明 |
|------|------|
| `backend/models/document.py` | Document, DocumentTemplate 模型 |
| `backend/api/schemas/document.py` | Schema |
| `backend/api/controllers/DocController.py` | 文档控制器 |
| `backend/api/router/v1/docs.py` | 路由 |
| 新增 API | `GET /v1/docs`, `POST /v1/docs/upload`, `POST /v1/docs/check-references`, `GET/POST /v1/docs/templates` |

### 1.4 模板库与主题库 ✅
| 文件 | 说明 |
|------|------|
| `backend/models/template_library.py` | Template, Theme 模型 |
| `backend/api/schemas/template_library.py` | Schema |
| `backend/api/controllers/TemplateLibraryController.py` | 模板库控制器 |
| `backend/api/controllers/ThemeLibraryController.py` | 主题库控制器 |
| `backend/api/router/v1/template_library.py` | 路由 |
| 新增 API | `GET/POST /v1/template-library`, `POST /v1/template-library/import`, `GET/POST /v1/theme-library`, `POST /v1/theme-library/import` |

### 1.5 Git 版本管理 ✅
| 文件 | 说明 |
|------|------|
| `backend/api/schemas/git.py` | Schema |
| `backend/api/controllers/GitController.py` | 对本地 Git 仓库的操作封装 |
| `backend/api/router/v1/git.py` | 路由 |
| 新增 API | `GET /v1/git/status`, `GET /v1/git/history`, `GET /v1/git/diff`, `POST /v1/git/commit`, `POST /v1/git/restore`, `POST /v1/git/workspace/init`, `POST /v1/git/workspace/push` 等 |

### 1.6 HTML 审查与编辑 ✅
| 文件 | 说明 |
|------|------|
| `backend/models/review_artifact.py` | ReviewDiagram, TextEdit 模型 |
| `backend/api/schemas/review.py` | Schema |
| `backend/api/controllers/HtmlReviewController.py` | HTML 审查控制器 |
| `backend/api/router/v1/html_review.py` | 路由 |
| 新增 API | `GET /v1/html-review/diagrams`, `POST /v1/html-review/diagram-drafts`, `POST /v1/html-review/text-edits`, `POST /v1/html-review/style-hack` |

### 1.7 审查报告 ✅
| 文件 | 说明 |
|------|------|
| `backend/models/review_report.py` | ReviewReport 模型 |
| `backend/api/schemas/review_report.py` | Schema |
| `backend/api/controllers/ReviewReportController.py` | 审查报告控制器 |
| `backend/api/router/v1/review_reports.py` | 路由 |
| 新增 API | `GET /v1/review-reports`, `POST /v1/review-reports/submit`, `POST /v1/review-reports/upload`, `POST /v1/review-reports/axhub-sync` |

### 1.8 网络访问控制 ✅
| 文件 | 说明 |
|------|------|
| `backend/models/access_control.py` | AccessToken, AccessLog 模型 |
| `backend/api/schemas/access.py` | Schema |
| `backend/api/controllers/AccessController.py` | 访问控制控制器 |
| `backend/api/router/v1/access.py` | 路由 |
| 新增 API | `GET /v1/access/status`, `POST /v1/access/password`, `POST /v1/access/login`, `POST /v1/access/share-token`, `POST /v1/access/validate` |

### 1.9 云发布与 Axhub 集成 ✅
| 文件 | 说明 |
|------|------|
| `backend/models/cloud_publish.py` | CloudPublishConfig, AxhubConnection 模型 |
| `backend/api/schemas/cloud_publish.py` | Schema |
| `backend/api/controllers/CloudPublishController.py` | 云发布控制器 |
| `backend/api/controllers/AxhubController.py` | Axhub 集成控制器 |
| `backend/api/router/v1/cloud_publish.py` | 路由 |
| 新增 API | `GET/POST /v1/cloud-publishing/config`, `POST /v1/cloud-publishing/publish`, `GET /v1/axhub/status`, `POST /v1/axhub/connect`, `POST /v1/axhub/disconnect`, `POST /v1/axhub/publish` |

### 1.10 AI 运行时与任务管理 ✅
| 文件 | 说明 |
|------|------|
| `backend/models/ai_runtime.py` | AIRun, AIGenerationTask 模型 |
| `backend/api/schemas/ai_runtime.py` | Schema |
| `backend/api/controllers/AIRuntimeController.py` | AI 运行时控制器 |
| `backend/api/router/v1/ai_runtime.py` | 路由 |
| 新增 API | `POST /v1/ai/runs`, `GET /v1/ai/runs/{id}`, `POST /v1/ai/generation-tasks`, `GET /v1/ai/artifact-history/assets` |

### 1.11 WebSocket 端点 ✅
| 文件 | 说明 |
|------|------|
| `backend/api/websocket/__init__.py` | 连接管理器 + 5 条桥接 |
| 路由 | `/api/canvas-bridge`, `/api/preview-bridge`, `/api/axhub-canvas-mcp`, `/api/axhub-preview-mcp`, `/api/opencode-bridge`, `GET /api/ws/clients` |

### 1.12 基础设施修复 ✅
- `api/responses/Base.py` 新增 `ORMModel` 基类（`from_attributes=True`），修复所有 Response schema 从 ORM 验证
- `config/db.py` 新增 `DATA_DIR`、`ACCESS_PASSWORD` 配置
- `tests/conftest.py` 修复 `:memory:` SQLite 的 loop 切换问题（改用临时文件）

---

## 阶段二：Vue 前端重写（✅ 已完成）

### 2.1 项目仪表盘（dashboard）✅
- 统计卡片行（项目/原型/标注/通道数）
- 项目列表（点击进入原型页）
- 发布通道状态卡 + 最近活动时间线

### 2.2 原型管理（prototypes）✅
- 项目选择卡片网格 + 原型列表表格
- 原型详情页：设备外壳（桌面/平板/手机）+ 画布 iframe
- AI 生成标注 + 标注 CRUD（元素级/页面级 + 颜色 + 过滤）

### 2.3 标注系统（annotations）✅
- 双粒度标注（element/page scope）
- 版本时间轴 + 创建版本 + 回滚

### 2.4 知识库（knowledge）✅
- 5 种条目类型 + 项目/团队双范围
- 全文搜索 + 类型过滤 + 分页
- AI 自动知识抽取（预览 + 确认导入）

### 2.5 AI 助手（ai）✅
- 对话区（chat + review 模式）+ 快捷提示
- Context Bundle 加载 + Prompt Pack 角色生成
- AI 运行记录 + 执行

### 2.6 发布管理（publish）✅
- 通道状态卡片（开发/评审/正式）+ 部署
- 部署记录表 + 云发布配置 + Axhub 连接状态

### 2.7 更多页面 ✅
- 设置页（访问控制 / Git / 模板主题 / 文件管理 4 菜单）
- 审查报告页（列表 / 提交 / 详情 / 编辑 / 评分进度环）

### 2.8 API 客户端 ✅
- `frontend/src/api/index.ts` 扩展 14 个 API 模块，覆盖全部新后端端点

---

## 阶段三：前后端联调（✅ 已完成）

### 3.1 验证结果
- ✅ 后端 28 项端点 TestClient 验证通过
- ✅ 后端 pytest 7 passed
- ✅ WebSocket 5 条桥接验证通过
- ✅ OpenAPI 88 个路径
- ✅ 前端 `vue-tsc --noEmit` 类型检查通过（修复 3 处类型错误）
- ✅ 前端 `npm run build` 构建成功（7.34s）

