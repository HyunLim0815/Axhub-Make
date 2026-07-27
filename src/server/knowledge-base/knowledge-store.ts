/**
 * Knowledge Base — 产品知识库
 *
 * 沉淀设计决策、术语表、约束条件等产品知识，
 * 让 AI 生成新原型时自动继承项目上下文。
 */

import fs from 'node:fs';
import path from 'node:path';

/* ─── Types ─────────────────────────────────────────── */

export type KnowledgeEntryType = 'term' | 'decision' | 'constraint' | 'user-feedback' | 'design-rule';

export interface KnowledgeEntry {
  id: string;
  type: KnowledgeEntryType;
  title: string;
  content: string;           // Markdown 正文
  tags: string[];
  source?: string;           // 来源（对话 ID / 原型 ID / 手动录入）
  createdAt: number;
  updatedAt: number;
  relatedEntryIds?: string[];
}

export interface KnowledgeBase {
  schemaVersion: 1;
  projectId: string;
  entries: KnowledgeEntry[];
  updatedAt: number;
}

/* ─── Store ─────────────────────────────────────────── */

const KB_DIR_NAME = '.axhub';
const KB_FILE_NAME = 'knowledge-base.json';

/** 获取知识库文件路径 */
export function getKnowledgeBasePath(projectRoot: string): string {
  return path.join(projectRoot, KB_DIR_NAME, KB_FILE_NAME);
}

/** 读取知识库，不存在则返回空知识库 */
export function readKnowledgeBase(projectRoot: string, projectId: string): KnowledgeBase {
  const filePath = getKnowledgeBasePath(projectRoot);
  if (!fs.existsSync(filePath)) {
    return createEmptyKnowledgeBase(projectId);
  }
  try {
    const raw = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    return normalizeKnowledgeBase(raw, projectId);
  } catch {
    return createEmptyKnowledgeBase(projectId);
  }
}

/** 写入知识库 */
export function writeKnowledgeBase(projectRoot: string, kb: KnowledgeBase): void {
  const filePath = getKnowledgeBasePath(projectRoot);
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  kb.updatedAt = Date.now();
  fs.writeFileSync(filePath, `${JSON.stringify(kb, null, 2)}\n`, 'utf8');
}

/** 创建空知识库 */
export function createEmptyKnowledgeBase(projectId: string): KnowledgeBase {
  return {
    schemaVersion: 1,
    projectId,
    entries: [],
    updatedAt: Date.now(),
  };
}

/** 规范化知识库数据 */
function normalizeKnowledgeBase(input: unknown, projectId: string): KnowledgeBase {
  const fallback = createEmptyKnowledgeBase(projectId);
  if (!input || typeof input !== 'object' || Array.isArray(input)) return fallback;

  const record = input as Record<string, unknown>;
  const entries = Array.isArray(record.entries)
    ? record.entries.filter((e): e is KnowledgeEntry => e && typeof e === 'object' && typeof (e as KnowledgeEntry).id === 'string')
    : [];

  return {
    schemaVersion: 1,
    projectId: typeof record.projectId === 'string' ? record.projectId : projectId,
    entries,
    updatedAt: typeof record.updatedAt === 'number' ? record.updatedAt : Date.now(),
  };
}

/* ─── CRUD ──────────────────────────────────────────── */

let _idCounter = 0;

function generateEntryId(): string {
  _idCounter += 1;
  return `kb-${Date.now()}-${_idCounter}`;
}

/** 获取所有知识条目 */
export function getAllEntries(projectRoot: string, projectId: string): KnowledgeEntry[] {
  return readKnowledgeBase(projectRoot, projectId).entries;
}

/** 按 ID 获取知识条目 */
export function getEntryById(projectRoot: string, projectId: string, entryId: string): KnowledgeEntry | null {
  const kb = readKnowledgeBase(projectRoot, projectId);
  return kb.entries.find((e) => e.id === entryId) ?? null;
}

/** 创建知识条目 */
export function createEntry(projectRoot: string, projectId: string, data: {
  type: KnowledgeEntryType;
  title: string;
  content: string;
  tags?: string[];
  source?: string;
}): KnowledgeEntry {
  const kb = readKnowledgeBase(projectRoot, projectId);
  const now = Date.now();
  const entry: KnowledgeEntry = {
    id: generateEntryId(),
    type: data.type,
    title: data.title.trim(),
    content: data.content.trim(),
    tags: data.tags ?? [],
    source: data.source,
    createdAt: now,
    updatedAt: now,
  };
  kb.entries.push(entry);
  writeKnowledgeBase(projectRoot, kb);
  return entry;
}

/** 更新知识条目 */
export function updateEntry(projectRoot: string, projectId: string, entryId: string, data: Partial<{
  type: KnowledgeEntryType;
  title: string;
  content: string;
  tags: string[];
  source: string;
}>): KnowledgeEntry | null {
  const kb = readKnowledgeBase(projectRoot, projectId);
  const entry = kb.entries.find((e) => e.id === entryId);
  if (!entry) return null;

  if (data.type !== undefined) entry.type = data.type;
  if (data.title !== undefined) entry.title = data.title.trim();
  if (data.content !== undefined) entry.content = data.content.trim();
  if (data.tags !== undefined) entry.tags = data.tags;
  if (data.source !== undefined) entry.source = data.source;
  entry.updatedAt = Date.now();

  writeKnowledgeBase(projectRoot, kb);
  return entry;
}

/** 删除知识条目 */
export function deleteEntry(projectRoot: string, projectId: string, entryId: string): boolean {
  const kb = readKnowledgeBase(projectRoot, projectId);
  const index = kb.entries.findIndex((e) => e.id === entryId);
  if (index < 0) return false;
  kb.entries.splice(index, 1);
  writeKnowledgeBase(projectRoot, kb);
  return true;
}

/** 搜索知识条目（按标题/内容/标签模糊匹配） */
export function searchEntries(projectRoot: string, projectId: string, query: string): KnowledgeEntry[] {
  const kb = readKnowledgeBase(projectRoot, projectId);
  const q = query.toLowerCase().trim();
  if (!q) return kb.entries;

  return kb.entries.filter((e) =>
    e.title.toLowerCase().includes(q)
    || e.content.toLowerCase().includes(q)
    || e.tags.some((t) => t.toLowerCase().includes(q))
    || e.type.toLowerCase().includes(q)
  );
}

/** 按类型过滤知识条目 */
export function getEntriesByType(projectRoot: string, projectId: string, type: KnowledgeEntryType): KnowledgeEntry[] {
  const kb = readKnowledgeBase(projectRoot, projectId);
  return kb.entries.filter((e) => e.type === type);
}
