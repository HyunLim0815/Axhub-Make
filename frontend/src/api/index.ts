import { ofetch } from 'ofetch'

export const api = ofetch.create({
  baseURL: '/',
  headers: { 'Content-Type': 'application/json' },
  onResponseError({ response }) {
    const msg = response._data?.message || response.statusText
    console.error('[api]', msg)
  },
})

// ── 项目 API ──

export const projectApi = {
  list: (page = 1, size = 10) => api('/v1/projects/', { params: { page, size } }),
  get: (id: number) => api(`/v1/projects/${id}`),
  create: (data: any) => api('/v1/projects/', { method: 'POST', body: data }),
  update: (id: number, data: any) => api(`/v1/projects/${id}`, { method: 'PUT', body: data }),
  delete: (id: number) => api(`/v1/projects/${id}`, { method: 'DELETE' }),
  listPrototypes: (projectId: number, page = 1, size = 10) =>
    api(`/v1/projects/${projectId}/prototypes`, { params: { page, size } }),
  createPrototype: (projectId: number, name = '新原型') =>
    api(`/v1/projects/${projectId}/prototypes`, { method: 'POST', params: { name } }),
}

// ── 原型 API ──

export const prototypeApi = {
  list: (params?: any) => api('/v1/prototypes/', { params }),
  get: (id: number) => api(`/v1/prototypes/${id}`),
  create: (data: any) => api('/v1/prototypes/', { method: 'POST', body: data }),
  update: (id: number, data: any) => api(`/v1/prototypes/${id}`, { method: 'PUT', body: data }),
  delete: (id: number) => api(`/v1/prototypes/${id}`, { method: 'DELETE' }),
}

// ── 标注 API ──

export const annotationApi = {
  list: (params?: any) => api('/v1/annotations/', { params }),
  get: (id: number) => api(`/v1/annotations/${id}`),
  create: (data: any) => api('/v1/annotations/', { method: 'POST', body: data }),
  update: (id: number, data: any) => api(`/v1/annotations/${id}`, { method: 'PUT', body: data }),
  delete: (id: number) => api(`/v1/annotations/${id}`, { method: 'DELETE' }),
  versions: (pid: number) => api(`/v1/annotations/versions/${pid}`),
  createVersion: (pid: number, data: any) =>
    api(`/v1/annotations/versions/${pid}`, { method: 'POST', body: data }),
  rollback: (pid: number, version: number) =>
    api(`/v1/annotations/versions/${pid}/rollback/${version}`, { method: 'POST' }),
}

// ── 知识库 API ──

export const knowledgeApi = {
  list: (params?: any) => api('/v1/knowledge/', { params }),
  get: (id: number) => api(`/v1/knowledge/${id}`),
  create: (data: any) => api('/v1/knowledge/', { method: 'POST', body: data }),
  update: (id: number, data: any) => api(`/v1/knowledge/${id}`, { method: 'PUT', body: data }),
  delete: (id: number) => api(`/v1/knowledge/${id}`, { method: 'DELETE' }),
  extract: (text: string, source = '') =>
    api('/v1/ai/agents/extract-knowledge', { method: 'POST', body: { text, source } }),
}

// ── 发布 API ──

export const publishApi = {
  channels: () => api('/v1/publish/channels'),
  updateChannel: (id: number, data: any) =>
    api(`/v1/publish/channels/${id}`, { method: 'PUT', body: data }),
  deploy: (id: number, summary = '') =>
    api(`/v1/publish/channels/${id}/deploy`, { method: 'POST', body: { summary } }),
  records: (channelId?: number) =>
    api('/v1/publish/records', { params: channelId ? { channel_id: channelId } : {} }),
  dashboard: () => api('/v1/publish/dashboard'),
}

// ── AI API ──

export const aiApi = {
  chat: (prompt: string, systemPrompt?: string) =>
    api('/v1/ai/chat', { method: 'POST', body: { prompt, system_prompt: systemPrompt } }),
  context: (prototypeId?: number) =>
    api('/v1/ai/context', { params: prototypeId ? { prototype_id: prototypeId } : {} }),
  promptPack: (role: string, prototypeId?: number) =>
    api('/v1/ai/prompt-pack', { params: { role, prototype_id: prototypeId } }),
  annotate: (prompt: string, elementInfo?: any) =>
    api('/v1/ai/agents/annotate', { method: 'POST', body: { prompt, element_info: elementInfo } }),
  review: (target: string, context?: string) =>
    api('/v1/ai/agents/review', { method: 'POST', body: { target, context } }),
  runs: (params?: any) => api('/v1/ai/runs', { params }),
  createRun: (data: any) => api('/v1/ai/runs', { method: 'POST', body: data }),
  executeRun: (id: number) => api(`/v1/ai/runs/${id}/execute`, { method: 'POST' }),
  generationTasks: (params?: any) => api('/v1/ai/generation-tasks', { params }),
  createGenerationTask: (data: any) => api('/v1/ai/generation-tasks', { method: 'POST', body: data }),
}

// ── 文件操作 API ──

export const fileApi = {
  list: (subDir = '') => api('/v1/files/list', { params: { sub_dir: subDir } }),
  upload: (file: File, subDir = '') => {
    const form = new FormData()
    form.append('file', file)
    form.append('sub_dir', subDir)
    return api('/v1/files/upload', { method: 'POST', body: form })
  },
  copy: (source: string, destination: string) =>
    api('/v1/files/copy', { method: 'POST', params: { source, destination } }),
  rename: (oldPath: string, newPath: string) =>
    api('/v1/files/rename', { method: 'POST', params: { old_path: oldPath, new_path: newPath } }),
  delete: (path: string) => api('/v1/files/delete', { method: 'POST', params: { path } }),
}

// ── 媒体 API ──

export const mediaApi = {
  list: (params?: any) => api('/v1/media/', { params }),
  upload: (file: File, folder = '') => {
    const form = new FormData()
    form.append('file', file)
    form.append('folder', folder)
    return api('/v1/media/upload', { method: 'POST', body: form })
  },
  createFolder: (name: string, parent = '') =>
    api('/v1/media/folder', { method: 'POST', body: { name, parent } }),
  delete: (id: number) => api(`/v1/media/${id}`, { method: 'DELETE' }),
}

// ── 文档 API ──

export const docApi = {
  list: (params?: any) => api('/v1/docs/', { params }),
  get: (id: number) => api(`/v1/docs/${id}`),
  create: (data: any) => api('/v1/docs/', { method: 'POST', body: data }),
  update: (id: number, data: any) => api(`/v1/docs/${id}`, { method: 'PUT', body: data }),
  delete: (id: number) => api(`/v1/docs/${id}`, { method: 'DELETE' }),
  templates: () => api('/v1/docs/templates'),
  createTemplate: (data: any) => api('/v1/docs/templates', { method: 'POST', body: data }),
  checkReferences: (content: string) =>
    api('/v1/docs/check-references', { method: 'POST', body: { content } }),
}

// ── 模板库 / 主题库 API ──

export const templateApi = {
  list: (params?: any) => api('/v1/template-library/', { params }),
  create: (data: any) => api('/v1/template-library/', { method: 'POST', body: data }),
  update: (id: number, data: any) => api(`/v1/template-library/${id}`, { method: 'PUT', body: data }),
  delete: (id: number) => api(`/v1/template-library/${id}`, { method: 'DELETE' }),
  import: (sourceUrl: string, name: string) =>
    api('/v1/template-library/import', { method: 'POST', body: { source_url: sourceUrl, name } }),
}

export const themeApi = {
  list: (params?: any) => api('/v1/theme-library/', { params }),
  create: (data: any) => api('/v1/theme-library/', { method: 'POST', body: data }),
  update: (id: number, data: any) => api(`/v1/theme-library/${id}`, { method: 'PUT', body: data }),
  delete: (id: number) => api(`/v1/theme-library/${id}`, { method: 'DELETE' }),
  import: (sourceUrl: string, name: string) =>
    api('/v1/theme-library/import', { method: 'POST', body: { source_url: sourceUrl, name } }),
}

// ── Git API ──

export const gitApi = {
  status: () => api('/v1/git/status'),
  history: (maxCount = 20) => api('/v1/git/history', { params: { max_count: maxCount } }),
  diff: (file = '', fromHash?: string, toHash?: string) =>
    api('/v1/git/diff', { params: { file, from_hash: fromHash, to_hash: toHash } }),
  commit: (message: string, paths?: string[]) =>
    api('/v1/git/commit', { method: 'POST', body: { message, paths } }),
  restore: (file: string, version?: string) =>
    api('/v1/git/restore', { method: 'POST', body: { file, version } }),
  initWorkspace: (path = '.') =>
    api('/v1/git/workspace/init', { method: 'POST', body: { path } }),
  setRemote: (url: string, name = 'origin') =>
    api('/v1/git/workspace/remote', { method: 'POST', body: { url, name } }),
  push: (remote = 'origin', branch = 'main') =>
    api('/v1/git/workspace/push', { method: 'POST', params: { remote, branch } }),
  fetch: () => api('/v1/git/workspace/fetch', { method: 'POST' }),
}

// ── 审查报告 API ──

export const reviewReportApi = {
  list: (params?: any) => api('/v1/review-reports/', { params }),
  get: (id: number) => api(`/v1/review-reports/${id}`),
  create: (data: any) => api('/v1/review-reports/', { method: 'POST', body: data }),
  update: (id: number, data: any) => api(`/v1/review-reports/${id}`, { method: 'PUT', body: data }),
  delete: (id: number) => api(`/v1/review-reports/${id}`, { method: 'DELETE' }),
  submit: (data: any) => api('/v1/review-reports/submit', { method: 'POST', body: data }),
  exists: (params?: any) => api('/v1/review-reports/exists', { params }),
  axhubSync: (reportId: number, axhubUrl: string) =>
    api('/v1/review-reports/axhub-sync', { method: 'POST', body: { report_id: reportId, axhub_url: axhubUrl } }),
}

// ── HTML 审查 API ──

export const htmlReviewApi = {
  diagrams: (params?: any) => api('/v1/html-review/diagrams', { params }),
  createDiagram: (data: any) => api('/v1/html-review/diagrams', { method: 'POST', body: data }),
  textEdits: (params?: any) => api('/v1/html-review/text-edits', { params }),
  createTextEdit: (data: any) => api('/v1/html-review/text-edits', { method: 'POST', body: data }),
  applyTextEdit: (id: number) => api(`/v1/html-review/text-edits/${id}/apply`, { method: 'POST' }),
  styleHack: (selector: string, css: string) =>
    api('/v1/html-review/style-hack', { method: 'POST', body: { selector, css } }),
}

// ── 访问控制 API ──

export const accessApi = {
  status: () => api('/v1/access/status'),
  setPassword: (password: string) =>
    api('/v1/access/password', { method: 'POST', body: { password } }),
  login: (password: string) => api('/v1/access/login', { method: 'POST', body: { password } }),
  createShareToken: (name = '', expiresInHours = 24) =>
    api('/v1/access/share-token', { method: 'POST', body: { name, expires_in_hours: expiresInHours } }),
  validate: (token: string) => api('/v1/access/validate', { method: 'POST', body: { token } }),
}

// ── 云发布 / Axhub API ──

export const cloudPublishApi = {
  configs: () => api('/v1/cloud-publishing/config'),
  createConfig: (data: any) => api('/v1/cloud-publishing/config', { method: 'POST', body: data }),
  updateConfig: (id: number, data: any) =>
    api(`/v1/cloud-publishing/config/${id}`, { method: 'PUT', body: data }),
  deleteConfig: (id: number) => api(`/v1/cloud-publishing/config/${id}`, { method: 'DELETE' }),
  publish: (configId: number, summary = '') =>
    api('/v1/cloud-publishing/publish', { method: 'POST', body: { config_id: configId, summary } }),
}

export const axhubApi = {
  status: () => api('/v1/axhub/status'),
  connect: (code: string, redirectUri = '') =>
    api('/v1/axhub/connect', { method: 'POST', body: { code, redirect_uri: redirectUri } }),
  disconnect: () => api('/v1/axhub/disconnect', { method: 'POST' }),
  publish: (projectId: number, summary = '') =>
    api('/v1/axhub/publish', { method: 'POST', body: { config_id: projectId, summary } }),
}
