import { ofetch } from 'ofetch'

export const api = ofetch.create({
  baseURL: '/',
  headers: { 'Content-Type': 'application/json' },
  onResponseError({ response }) {
    const msg = response._data?.message || response.statusText
    window.$message?.error(msg)
  },
})

// ── 原型 API ──

export const prototypeApi = {
  list: (page = 1, size = 10) => api('/v1/prototypes/', { params: { page, size } }),
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
}

// ── 知识库 API ──

export const knowledgeApi = {
  list: (params?: any) => api('/v1/knowledge/', { params }),
  get: (id: number) => api(`/v1/knowledge/${id}`),
  create: (data: any) => api('/v1/knowledge/', { method: 'POST', body: data }),
  update: (id: number, data: any) => api(`/v1/knowledge/${id}`, { method: 'PUT', body: data }),
  delete: (id: number) => api(`/v1/knowledge/${id}`, { method: 'DELETE' }),
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
}
