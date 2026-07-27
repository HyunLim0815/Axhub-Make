/**
 * 知识库 HTTP API 路由
 *
 * 路由列表：
 *   GET    /api/knowledge-base?projectId=<id>[&q=<query>][&type=<type>] — 查询条目
 *   GET    /api/knowledge-base/context?projectId=<id>[&prototype=<name>] — 获取 Prompt 上下文
 *   POST   /api/knowledge-base/entries — 创建条目
 *   PUT    /api/knowledge-base/entries/:id — 更新条目
 *   DELETE /api/knowledge-base/entries/:id — 删除条目
 */

import type { IncomingMessage, ServerResponse } from 'node:http';

import { readJsonBody, sendCorsJson, sendCorsPreflight } from '../http.ts';
import {
  getAllEntries,
  getEntryById,
  createEntry,
  updateEntry,
  deleteEntry,
  searchEntries,
  getEntriesByType,
  type KnowledgeEntryType,
  type KnowledgeBase,
} from './knowledge-store.ts';
import { getPrototypeGenerationContext } from './knowledge-context.ts';

export interface KnowledgeBaseContext {
  projectRoot: string;
  projectId: string;
}

/** 解析 URL 路径中的知识库条目 ID */
function parseEntryId(url: URL): string | null {
  // 匹配 /api/knowledge-base/entries/<id>
  const match = url.pathname.match(/^\/api\/knowledge-base\/entries\/([^/]+)$/);
  return match ? match[1] : null;
}

/** 查询参数提取 */
function parseQueryParams(url: URL): { q?: string; type?: KnowledgeEntryType } {
  const q = url.searchParams.get('q')?.trim() || undefined;
  const type = url.searchParams.get('type') as KnowledgeEntryType | undefined;
  return { q, type };
}

export function handleKnowledgeBaseApi(
  req: IncomingMessage,
  res: ServerResponse,
  context: KnowledgeBaseContext,
  url: URL,
): boolean {
  // 只处理 /api/knowledge-base 路径
  if (!url.pathname.startsWith('/api/knowledge-base')) return false;

  if (req.method === 'OPTIONS') {
    sendCorsPreflight(res);
    return true;
  }

  const { projectRoot, projectId } = context;

  // ── 条目操作路由 ──
  const entryId = parseEntryId(url);

  // GET /api/knowledge-base/entries/:id — 获取单条条目
  if (entryId && req.method === 'GET') {
    const entry = getEntryById(projectRoot, projectId, entryId);
    if (!entry) {
      sendCorsJson(res, { error: 'Entry not found' }, { status: 404 });
    } else {
      sendCorsJson(res, { ok: true, entry });
    }
    return true;
  }

  // POST /api/knowledge-base/entries — 创建条目
  if (!entryId && url.pathname === '/api/knowledge-base/entries' && req.method === 'POST') {
    readJsonBody(req)
      .then((body) => {
        if (!body || typeof body !== 'object') {
          sendCorsJson(res, { error: 'Invalid request body' }, { status: 400 });
          return;
        }
        const data = body as Record<string, unknown>;
        const type = String(data.type ?? '').trim() as KnowledgeEntryType;
        const title = String(data.title ?? '').trim();
        const content = String(data.content ?? '').trim();
        const tags = Array.isArray(data.tags) ? data.tags.map(String) : [];
        const source = data.source ? String(data.source).trim() : undefined;

        if (!type || !title || !content) {
          sendCorsJson(res, { error: 'Missing required fields: type, title, content' }, { status: 400 });
          return;
        }

        const validTypes: KnowledgeEntryType[] = ['term', 'decision', 'constraint', 'user-feedback', 'design-rule'];
        if (!validTypes.includes(type as KnowledgeEntryType)) {
          sendCorsJson(res, { error: `Invalid type. Must be one of: ${validTypes.join(', ')}` }, { status: 400 });
          return;
        }

        const entry = createEntry(projectRoot, projectId, { type: type as KnowledgeEntryType, title, content, tags, source });
        sendCorsJson(res, { ok: true, entry });
      })
      .catch((error) => sendCorsJson(res, { error: error?.message || 'Failed to create entry' }, { status: 400 }));
    return true;
  }

  // PUT /api/knowledge-base/entries/:id — 更新条目
  if (entryId && req.method === 'PUT') {
    readJsonBody(req)
      .then((body) => {
        if (!body || typeof body !== 'object') {
          sendCorsJson(res, { error: 'Invalid request body' }, { status: 400 });
          return;
        }
        const data = body as Record<string, unknown>;
        const updated = updateEntry(projectRoot, projectId, entryId, {
          type: data.type as KnowledgeEntryType | undefined,
          title: data.title as string | undefined,
          content: data.content as string | undefined,
          tags: Array.isArray(data.tags) ? data.tags.map(String) : undefined,
          source: data.source as string | undefined,
        });
        if (!updated) {
          sendCorsJson(res, { error: 'Entry not found' }, { status: 404 });
        } else {
          sendCorsJson(res, { ok: true, entry: updated });
        }
      })
      .catch((error) => sendCorsJson(res, { error: error?.message || 'Failed to update entry' }, { status: 400 }));
    return true;
  }

  // DELETE /api/knowledge-base/entries/:id — 删除条目
  if (entryId && req.method === 'DELETE') {
    const deleted = deleteEntry(projectRoot, projectId, entryId);
    if (!deleted) {
      sendCorsJson(res, { error: 'Entry not found' }, { status: 404 });
    } else {
      sendCorsJson(res, { ok: true });
    }
    return true;
  }

  // ── 列表/搜索/过滤/上下文路由 ──

  // GET /api/knowledge-base/context — 获取原型生成上下文
  if (!entryId && url.pathname === '/api/knowledge-base/context' && req.method === 'GET') {
    const prototypeName = url.searchParams.get('prototype') || undefined;
    const context = getPrototypeGenerationContext(projectRoot, projectId, prototypeName);
    sendCorsJson(res, { ok: true, context });
    return true;
  }

  // GET /api/knowledge-base — 查询条目
  if (!entryId && url.pathname === '/api/knowledge-base' && req.method === 'GET') {
    const { q, type } = parseQueryParams(url);

    let entries;
    if (q) {
      entries = searchEntries(projectRoot, projectId, q);
    } else if (type) {
      entries = getEntriesByType(projectRoot, projectId, type);
    } else {
      entries = getAllEntries(projectRoot, projectId);
    }

    sendCorsJson(res, { ok: true, entries, total: entries.length });
    return true;
  }

  sendCorsJson(res, { error: 'Method not allowed' }, { status: 405 });
  return true;
}
