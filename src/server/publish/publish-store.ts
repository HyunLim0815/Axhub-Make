/**
 * 发布通道模型 — 多环境部署管理
 */

import fs from 'node:fs';
import path from 'node:path';

/* ─── Types ─────────────────────────────────────────── */

export type PublishChannelType = 'development' | 'review' | 'production';

export type PublishStatus = 'pending' | 'publishing' | 'published' | 'failed';

export interface PublishChannel {
  id: string;
  name: string;
  type: PublishChannelType;
  baseUrl?: string;
  accessControl: 'public' | 'team' | 'invite-only';
  currentVersion?: number;
  publishedAt?: number;
  status: PublishStatus;
  createdAt: number;
  updatedAt: number;
}

export interface PublishRecord {
  id: string;
  channelId: string;
  version: number;
  summary: string;
  status: PublishStatus;
  error?: string;
  createdAt: number;
  completedAt?: number;
}

export interface PublishConfig {
  schemaVersion: 1;
  projectId: string;
  channels: PublishChannel[];
  records: PublishRecord[];
  updatedAt: number;
}

/* ─── Store ─────────────────────────────────────────── */

const PUBLISH_DIR = '.axhub';
const PUBLISH_FILE = 'publish.json';

function getPublishPath(projectRoot: string): string {
  return path.join(projectRoot, PUBLISH_DIR, PUBLISH_FILE);
}

export function readPublishConfig(projectRoot: string, projectId: string): PublishConfig {
  const filePath = getPublishPath(projectRoot);
  if (!fs.existsSync(filePath)) return createDefaultConfig(projectId);
  try {
    const raw = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    return normalizeConfig(raw, projectId);
  } catch {
    return createDefaultConfig(projectId);
  }
}

function writePublishConfig(projectRoot: string, config: PublishConfig): void {
  const filePath = getPublishPath(projectRoot);
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  config.updatedAt = Date.now();
  fs.writeFileSync(filePath, `${JSON.stringify(config, null, 2)}\n`, 'utf8');
}

function createDefaultConfig(projectId: string): PublishConfig {
  return {
    schemaVersion: 1,
    projectId,
    channels: [
      { id: 'dev', name: '开发版', type: 'development', accessControl: 'team', status: 'pending', createdAt: Date.now(), updatedAt: Date.now() },
      { id: 'review', name: '评审版', type: 'review', accessControl: 'invite-only', status: 'pending', createdAt: Date.now(), updatedAt: Date.now() },
      { id: 'production', name: '正式版', type: 'production', accessControl: 'public', status: 'pending', createdAt: Date.now(), updatedAt: Date.now() },
    ],
    records: [],
    updatedAt: Date.now(),
  };
}

function normalizeConfig(input: unknown, projectId: string): PublishConfig {
  const fallback = createDefaultConfig(projectId);
  if (!input || typeof input !== 'object') return fallback;
  const record = input as Record<string, unknown>;
  return {
    schemaVersion: 1,
    projectId: typeof record.projectId === 'string' ? record.projectId : projectId,
    channels: Array.isArray(record.channels) ? record.channels.filter((c: unknown): c is PublishChannel => c && typeof c === 'object') : fallback.channels,
    records: Array.isArray(record.records) ? record.records.filter((r: unknown): r is PublishRecord => r && typeof r === 'object') : [],
    updatedAt: typeof record.updatedAt === 'number' ? record.updatedAt : Date.now(),
  };
}

/* ─── CRUD ──────────────────────────────────────────── */

let _idCounter = 0;
function genId(): string { _idCounter++; return `pub-${Date.now()}-${_idCounter}`; }

export function getChannels(projectRoot: string, projectId: string): PublishChannel[] {
  return readPublishConfig(projectRoot, projectId).channels;
}

export function updateChannel(projectRoot: string, projectId: string, channelId: string, data: Partial<Pick<PublishChannel, 'name' | 'baseUrl' | 'accessControl'>>): PublishChannel | null {
  const config = readPublishConfig(projectRoot, projectId);
  const channel = config.channels.find((c) => c.id === channelId);
  if (!channel) return null;
  if (data.name !== undefined) channel.name = data.name;
  if (data.baseUrl !== undefined) channel.baseUrl = data.baseUrl;
  if (data.accessControl !== undefined) channel.accessControl = data.accessControl;
  channel.updatedAt = Date.now();
  writePublishConfig(projectRoot, config);
  return channel;
}

export function deployToChannel(projectRoot: string, projectId: string, channelId: string, summary?: string): PublishRecord | null {
  const config = readPublishConfig(projectRoot, projectId);
  const channel = config.channels.find((c) => c.id === channelId);
  if (!channel) return null;

  const version = (channel.currentVersion ?? 0) + 1;
  const record: PublishRecord = {
    id: genId(),
    channelId,
    version,
    summary: summary || `v${version} 发布`,
    status: 'published',
    createdAt: Date.now(),
    completedAt: Date.now(),
  };

  channel.currentVersion = version;
  channel.publishedAt = Date.now();
  channel.status = 'published';
  channel.updatedAt = Date.now();
  config.records.push(record);

  writePublishConfig(projectRoot, config);
  return record;
}

export function getChannelRecords(projectRoot: string, projectId: string, channelId?: string): PublishRecord[] {
  const config = readPublishConfig(projectRoot, projectId);
  return channelId ? config.records.filter((r) => r.channelId === channelId) : config.records;
}

export function getLatestRecords(projectRoot: string, projectId: string, limit = 10): PublishRecord[] {
  const config = readPublishConfig(projectRoot, projectId);
  return config.records.slice(-limit).reverse();
}
