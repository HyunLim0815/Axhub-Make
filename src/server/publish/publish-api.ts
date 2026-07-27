/**
 * 发布管理 HTTP API
 *
 * 路由：
 *   GET    /api/publish/channels?projectId=<id> — 获取通道列表
 *   PUT    /api/publish/channels/:id?projectId=<id> — 更新通道
 *   POST   /api/publish/channels/:id/deploy?projectId=<id> — 部署到通道
 *   GET    /api/publish/records?projectId=<id>[&channel=<id>] — 发布记录
 *   GET    /api/publish/dashboard?projectId=<id> — 仪表盘数据
 */

import type { IncomingMessage, ServerResponse } from 'node:http';

import { readJsonBody, sendCorsJson, sendCorsPreflight } from '../http.ts';
import { getChannels, updateChannel, deployToChannel, getChannelRecords, getLatestRecords } from './publish-store.ts';

export interface PublishContext {
  projectRoot: string;
  projectId: string;
}

function requireProjectId(url: URL, res: ServerResponse): string | null {
  const pid = url.searchParams.get('projectId');
  if (!pid) { sendCorsJson(res, { error: 'Missing projectId' }, { status: 400 }); return null; }
  return pid;
}

export function handlePublishApi(
  req: IncomingMessage,
  res: ServerResponse,
  context: PublishContext,
  url: URL,
): boolean {
  if (!url.pathname.startsWith('/api/publish')) return false;
  if (req.method === 'OPTIONS') { sendCorsPreflight(res); return true; }

  const { projectRoot } = context;
  const projectId = requireProjectId(url, res);
  if (!projectId) return true;

  // GET /api/publish/channels
  if (url.pathname === '/api/publish/channels' && req.method === 'GET') {
    const channels = getChannels(projectRoot, projectId);
    sendCorsJson(res, { ok: true, channels });
    return true;
  }

  // PUT /api/publish/channels/:id
  const channelUpdateMatch = url.pathname.match(/^\/api\/publish\/channels\/([^/]+)$/);
  if (channelUpdateMatch && req.method === 'PUT') {
    readJsonBody(req).then((body) => {
      const data = body as Record<string, unknown> || {};
      const updated = updateChannel(projectRoot, projectId, channelUpdateMatch[1], {
        name: data.name as string,
        baseUrl: data.baseUrl as string,
        accessControl: data.accessControl as 'public' | 'team' | 'invite-only',
      });
      if (!updated) { sendCorsJson(res, { error: 'Channel not found' }, { status: 404 }); return; }
      sendCorsJson(res, { ok: true, channel: updated });
    }).catch((e) => sendCorsJson(res, { error: e.message }, { status: 400 }));
    return true;
  }

  // POST /api/publish/channels/:id/deploy
  const deployMatch = url.pathname.match(/^\/api\/publish\/channels\/([^/]+)\/deploy$/);
  if (deployMatch && req.method === 'POST') {
    readJsonBody(req).then((body) => {
      const summary = body && typeof body === 'object' ? String((body as Record<string, unknown>).summary ?? '') : '';
      const record = deployToChannel(projectRoot, projectId, deployMatch[1], summary || undefined);
      if (!record) { sendCorsJson(res, { error: 'Channel not found' }, { status: 404 }); return; }
      sendCorsJson(res, { ok: true, record });
    }).catch((e) => sendCorsJson(res, { error: e.message }, { status: 400 }));
    return true;
  }

  // GET /api/publish/records
  if (url.pathname === '/api/publish/records' && req.method === 'GET') {
    const channelId = url.searchParams.get('channel') || undefined;
    const records = channelId ? getChannelRecords(projectRoot, projectId, channelId) : getLatestRecords(projectRoot, projectId);
    sendCorsJson(res, { ok: true, records });
    return true;
  }

  // GET /api/publish/dashboard
  if (url.pathname === '/api/publish/dashboard' && req.method === 'GET') {
    const channels = getChannels(projectRoot, projectId);
    const latestRecords = getLatestRecords(projectRoot, projectId);
    sendCorsJson(res, {
      ok: true,
      channels: channels.map((c) => ({
        id: c.id, name: c.name, type: c.type, baseUrl: c.baseUrl,
        currentVersion: c.currentVersion, status: c.status, publishedAt: c.publishedAt,
      })),
      latestRecords,
      totalDeploys: latestRecords.length,
    });
    return true;
  }

  sendCorsJson(res, { error: 'Method not allowed' }, { status: 405 });
  return true;
}
